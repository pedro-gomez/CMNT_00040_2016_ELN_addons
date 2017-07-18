# -*- coding: utf-8 -*-
# Copyright 2017 El Nogal - Pedro Gómez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, models, fields, api, exceptions
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil import tz

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        invoices = self.filtered(
            lambda i: (
                not i.company_id.sii_test and
                i.company_id.sii_method == 'auto' and
                i.company_id.sii_check_invoice_date and
                i.sii_enabled and
                i.date_invoice >= '2017-07-01' and
                i.sii_state == 'not_sent'
            )
        )
        for invoice in invoices:
            date_to_send = None
            company = invoice.company_id
            if company.use_connector:
                date_to_send = company._get_sii_eta()
            invoice._sii_check_invoice_date(date_to_send)
        return res

    @api.multi
    def _sii_check_invoice_date(self, date_to_send=None):
        self.ensure_one()
        date_to_send = (date_to_send and
                        date_to_send or
                        datetime.now()
                        )
        user_tz = self.env.context.get('tz', self.env.user.partner_id.tz)
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(user_tz)
        date_to_send = date_to_send.replace(tzinfo=from_zone).astimezone(to_zone)
        date_to_send = datetime.strftime(date_to_send, '%Y-%m-%d')

        add_days = 8 if self.date_invoice <= '2017-12-31' else 4
        max_date = datetime.strptime(self.date_invoice, DEFAULT_SERVER_DATE_FORMAT)
        while add_days > 0:
            max_date += timedelta(days=1)
            weekday = max_date.weekday()
            if weekday >= 5: # Sábado y Domingo
                continue
            add_days -= 1
        max_date = max_date.strftime('%Y-%m-%d')
        if max_date < date_to_send:
            raise exceptions.Warning(_(
                'You can not communicate this invoice to SII '
                'because the date is not valid!'))
