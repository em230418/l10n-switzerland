<?xml version='1.0' encoding='UTF-8'?>
<%block name="root">\
<Document xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
</%block>\
\
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>${order.reference}</MsgId>
      <CreDtTm>${thetime.strftime("%Y-%m-%dT%H:%M:%S")}</CreDtTm>
      <NbOfTxs>${len (order.line_ids)}</NbOfTxs>
      <CtrlSum>${order.total}</CtrlSum>\
      <%block name="InitgPty">
        <InitgPty>
          <Nm>${order.user_id.company_id.name}</Nm>\
          ${address(order.user_id.company_id.partner_id)}\
        </InitgPty>\
      </%block>
    </GrpHdr>\
<%doc>\
  for each payment in the payment order
  line is saved in sepa_context in order to be available
  in sub blocks and inheritages. Because, for now, only unamed
  blocks and def in mako can use a local for loop variable.
</%doc>\
% for line in order.line_ids:
  <% sepa_context['line'] = line %>\
  <%block name="PmtInf">\
    <%
    line = sepa_context['line']
    today = thetime.strftime("%Y-%m-%d")
    %>
      <PmtInf>
        <PmtInfId>${line.name}</PmtInfId>
        <PmtMtd>TRF</PmtMtd>
        <BtchBookg>false</BtchBookg>
        <ReqdExctnDt>${line.date > today and line.date or today}</ReqdExctnDt>
        <Dbtr>
          <Nm>order.user_id.company_id.name</Nm>\
          ${address(order.user_id.company_id.partner_id)}\
        </Dbtr>
        <DbtrAcct>\
          ${acc_id(order.mode.bank_id)}\
        </DbtrAcct>
        <DbtrAgt>
          <FinInstnId>
            <BIC>${order.mode.bank_id.bank.bic}</BIC>
          </FinInstnId>
        </DbtrAgt>
        <CdtTrfTxInf>
          <PmtId>
            <EndToEndId>${line.name}</EndToEndId>
          </PmtId>
          <Amt>
            <InstdAmt Ccy="${line.currency.name}">${line.amount_currency}</InstdAmt>
          </Amt>
          <ChrgBr>SLEV</ChrgBr>
          <CdtrAgt>
            <FinInstnId>
              <BIC>${line.bank_id.bank.bic}</BIC>
            </FinInstnId>
          </CdtrAgt>
          <Cdtr>
            <Nm>${line.partner_id.name}</Nm>\
            ${address(line.partner_id)}\
          </Cdtr>
          <CdtrAcct>\
            ${acc_id(line.bank_id)}\
          </CdtrAcct>\
          <%block name="RmtInf"/>
        </CdtTrfTxInf>
      </PmtInf>\
  </%block>
% endfor
\
  </CstmrCdtTrfInitn>
</Document>
\
<%def name="address(partner)">\
              <PstlAdr>
                <StrtNm>${partner.street}</StrtNm>
                <PstCd>${partner.zip}</PstCd>
                <TwnNm>${partner.city}</TwnNm>
                <Ctry>${partner.country_id.code}</Ctry>
              </PstlAdr>
</%def>\
\
<%def name="acc_id(bank_acc)">
              <Id>
                % if bank_acc.iban:
                  <IBAN>${bank_acc.iban}</IBAN>
                % else:
                  <Othr>
                    <Id>${bank_acc.get_account_number()}</Id>
                  </Othr>
                % endif
              </Id>
</%def>