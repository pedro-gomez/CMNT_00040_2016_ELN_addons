# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv, fields
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta
import calendar
import time

class get_sales_forecast(osv.osv_memory):
    _name = 'get.sales.forecast'
    _description = 'Preload a sales forecast'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'account_id': fields.many2one('account.analytic.account', 'Account', required=True),
        'include_child_ids': fields.boolean('Include Child Accounts'),
        'include_refunds': fields.boolean('Include Refunds'),
        'percent_increase': fields.float('% Increase', digits=(16,2)),
        'date_start': fields.date('Start Date'),
    }
    _defaults = {
        'include_child_ids': True,
        'include_refunds': True,
    }

    def default_get(self, cr, uid, fields, context=None):
        """ Get default values
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for default value
        @param context: A standard dictionary
        @return: default values of fields
        """
        if context is None:
            context = {}
        res = super(get_sales_forecast, self).default_get(cr, uid, fields, context=context)
        date_today = datetime.now()
        date_start = date(year=date_today.year, month=1, day=1) - relativedelta(years=1)
        res.update({'date_start': date_start.strftime('%Y-%m-%d')})
        return res

    def get_sales_forecast(self, cr, uid, ids, context=None):
        """ Get forecast sales for the selected analytic account and,
                    which may also increase profits in the percentage selected."""

        if context is None:
            context = {}
        
        new_id = False

        products = {}

        invoice_ids = []
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                  'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

        inv_obj = self.pool.get('account.invoice')
        forecast_obj = self.pool.get('sales.forecast')
        forecast_line_obj = self.pool.get('sales.forecast.line')
        user_obj = self.pool.get('res.users')
        analytic_obj = self.pool.get('account.analytic.account')
        
        company_id = user_obj.browse(cr, uid, uid).company_id.id

        for form in self.browse(cr, uid, ids):
            form_analytic_ids = []
            new_analytic_ids = [form.account_id.id]
            if form.include_child_ids:
                while new_analytic_ids:
                    form_analytic_ids += new_analytic_ids
                    analytic_ids = new_analytic_ids
                    new_analytic_ids = []
                    for account in analytic_obj.browse(cr, uid, analytic_ids, context=context):
                        new_analytic_ids += map(lambda x: x.id, [child for child in account.child_ids if child.state != 'template'])
            else:
                form_analytic_ids = [form.account_id.id]
        
            #create forecast sales without lines
            date_from = datetime.strptime(form.date_start, '%Y-%m-%d') + relativedelta(day=1)
            date_to = datetime.strptime(form.date_start, '%Y-%m-%d') + relativedelta(day=31, months=11)
            forecast_name = '%s - (from: %s to: %s)' % (form.name, date_from.strftime('%d-%m-%Y'), date_to.strftime('%d-%m-%Y'))
            new_id = forecast_obj.create(cr, uid, {'name': forecast_name,
                                                   'analytic_id': form.account_id.id,
                                                   'commercial_id': uid,
                                                   'date': time.strftime('%d-%m-%Y'),
                                                   'company_id': company_id,
                                                   'state': 'draft'
                                                    })
            for month in range(0, 12):
                #I find all the invoices for each month in one year.
                date_from = datetime.strptime(form.date_start, '%Y-%m-%d') + relativedelta(months=month, day=1)
                date_to = datetime.strptime(form.date_start, '%Y-%m-%d') + relativedelta(months=month, day=31)
                domain = \
                    [('date_invoice', '>=', date_from.strftime('%d-%m-%Y')),
                    ('date_invoice', '<=', date_to.strftime('%d-%m-%Y')),
                    ('state', 'in', ['open', 'paid']),
                    ('company_id', '=', company_id)]
                if form.include_refunds:
                    domain += [('type', 'in', ['out_invoice', 'out_refund'])]
                else:
                    domain += [('type', '=', 'out_invoice')]
                invoice_ids = inv_obj.search(cr, uid, domain)
                if invoice_ids:
                    #If invoices, step through lines that share the selected
                    #analytic account and save them in a dictionary, with the
                    #id of product of the line like key:
                    #{Product_Id: [(amount, benefits)]}
                    for inv in inv_obj.browse(cr, uid, invoice_ids):
                        sign = inv.type in ['in_refund', 'out_refund'] and -1 or 1
                        for line in inv.invoice_line:
                            if line.account_analytic_id and line.product_id and line.account_analytic_id.id in form_analytic_ids:
                                quantity = self.pool.get('product.uom')._compute_qty(cr, uid, line.uos_id.id,line.quantity, line.product_id.uom_id.id)
                                if products.get(line.product_id.id):
                                    new_val = (products[line.product_id.id][0][0] + sign * quantity,
                                               products[line.product_id.id][0][1] + sign * line.price_subtotal)
                                    products[line.product_id.id][0] = new_val
                                else:
                                    products[line.product_id.id] = []
                                    products[line.product_id.id].append((sign * quantity, sign * line.price_subtotal))
                    if products:
                        for product in products:
                            if form.percent_increase:
                                #Calculation percentage increase
                                qty = products[product][0][0] + \
                                    ((form.percent_increase / 100) * \
                                    products[product][0][0])
                            else:
                                qty = products[product][0][0]

                            cur_forecast = forecast_obj.browse(cr, uid, new_id)
                            l_products = forecast_line_obj.search(cr, uid,
                                [('product_id','=', product),
                                ('sales_forecast_id', '=', cur_forecast.id)])
                            #If there are already lines created for the same product,
                            #update the quantities. Else, I create a new line
                            if l_products:
                                l = forecast_line_obj.browse(cr, uid, l_products[0])
                                if l.product_id.id == product:
                                    forecast_line_obj.write(cr, uid, l.id,
                                        {months[month] + '_qty': (qty + \
                                        (eval('o.' + (months[month] + '_qty'),{'o': l})))})
                            else:
                                forecast_line_obj.create(cr, uid, {
                                    'sales_forecast_id': new_id,
                                    'product_id': product,
                                    months[month] + '_qty': qty})
                        products = {}

        value = {
                'domain': str([('id', 'in', [new_id])]),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sales.forecast',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id': new_id
                }

        return value

get_sales_forecast()
