# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com)
# All Right Reserved
#
# Author : Yannick Vaucher (Camptocamp)
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import os
import time

from mako import exceptions
from mako.template import Template
from mako.lookup import TemplateLookup

import pooler
import addons
from osv import osv
from tools.translate import _

from msg_sepa import *

class Pain001(MsgSEPA):

    _DEFAULT_XSD_PATH = os.path.join('l10n_ch_sepa', 'base_sepa', 'base_xsd', 'pain.001.001.03.xsd')
    _BASE_TMPL_DIR = os.path.join('l10n_ch_sepa', 'base_sepa', 'base_template')
    _DEFAULT_TMPL_NAME = 'pain.001.001.03.xml.mako'

    _data = {}

    def __init__(self, xsd_path = _DEFAULT_XSD_PATH,
                       tmpl_dirs = [],
                       tmpl_name = _DEFAULT_TMPL_NAME):
        '''tmpl_path : path to mako template'''

        dirs = [addons.get_module_resource(self._BASE_TMPL_DIR)]
        for dir in tmpl_dirs:
            dirs += [addons.get_module_resource(dir)]

        lookup = TemplateLookup(directories=dirs, input_encoding='utf-8', output_encoding='utf-8')
        self.mako_tpl = lookup.get_template(tmpl_name)
        self._xml_data = None

        xsd_path = addons.get_module_resource(xsd_path)
        super(Pain001, self).__init__(xsd_path)

    def _check_data(self):
        '''
        Do all data check to ensure no data is missing to generate the XML file
        '''
        if not self._data:
            raise osv.except_osv(_('Error'), _('No data has been entered'))

        if not self._data['payment']:
            raise osv.except_osv(_('Error'), _('A payment order is missing'))
        payment = self._data['payment']

        if payment.state in ['draft']:
            raise osv.except_osv(_('ErrorPaymentState'), _('Payment is in draft state. Please confirm it first.'))

        cp_bank_acc = payment.mode.bank_id
        if not cp_bank_acc:
            raise osv.except_osv(_('ErrorCompanyBank'),
                                 _('No company bank is defined in payment'))
        if not cp_bank_acc.bank.bic:
            raise osv.except_osv(_('ErrorCompanyBankBIC'),
                                 _('The selected company bank has no BIC number'))
        if not cp_bank_acc.iban and \
           not cp_bank_acc.acc_number:
            raise osv.except_osv(_('ErrorCompanyBankAccNumber'),
                                 _('The selected company bank has no IBAN and no Account number'))

        #Check each invoices
        for line in payment.line_ids:
            crd_bank_acc = line.bank_id
            if not crd_bank_acc:
                raise osv.except_osv(_('ErrorCreditorBank'),
                                     _('No bank selected for creditor of invoice %s') %(line.name,))
            if not crd_bank_acc.bank.bic:
                raise osv.except_osv(_('ErrorCreditorBankBIC'),
                                     _('Creditor bank has no BIC number for invoice %s') %(line.name,))
            if not crd_bank_acc.iban and \
               not crd_bank_acc.acc_number:
                raise osv.except_osv(_('ErrorCompanyBankAccNumber'),
                                     _('The selected company bank has no IBAN and no Account number'))

    def _gather_payment_data(self, cursor, user, id, context=None):
        '''
        Record the payment order data based on its id
        '''
        context = context or {}

        pool = pooler.get_pool(cursor.dbname)
        payment_obj = pool.get('payment.order')

        payment = payment_obj.browse(cursor, user, id, context=context)
        self._data['payment'] = payment

    def compute_export(self, cursor, user, id, context=None):
        '''Compute the payment order 'id' as xml data using mako template'''
        context = context or {}

        self._gather_payment_data(cursor, user, id, context)
        self._check_data()

        try:
            self._xml_data = self.mako_tpl.render_unicode(order=self._data['payment'],
                                                          thetime = time,
                                                          sepa_context={})
        except Exception:
            raise Exception(exceptions.text_error_template().render())


        if not self._xml_data:
            raise osv.except_osv(_('XML is Empty !'),
                                 _('An error has occured during XML generation'))

        # Validate the XML generation
        if not self._is_xsd_valid():
            raise osv.except_osv(_('XML is not Valid !'),
                                 _('An error has occured during XML generation'))


        return self._xml_data

MsgSEPAFactory.register_class('pain.001', Pain001)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: