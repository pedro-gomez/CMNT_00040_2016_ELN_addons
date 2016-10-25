# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2016 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp import models, fields, api


class InventoryReportBetweenDatesXlsWzd(models.TransientModel):
    _name = 'inventory.report.between.dates.xls.wzd'

    date_from = fields.Date('From Date', required=True, default=fields.Date.today())
    date_to = fields.Date('To Date', required=True, default=fields.Date.today())
    location_id = fields.Many2one('stock.location', 'Location', required=True)

    @api.multi
    def _get_report_data(self):
        list_product = {}
        date_start = self.date_from
        date_end = self.date_to
        location_outsource = self.location_id.id
        sql_from = '''
            SELECT product_id, name, code, sum(product_qty_in - product_qty_out) as qty_from
                FROM (SELECT sm.product_id, pt.name, pp.default_code as code,
                    COALESCE(sum(sm.product_qty), 0) AS product_qty_in,
                    0 AS product_qty_out
                FROM stock_move sm
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day', COALESCE(sm.effective_date, sm.date)) < '%s'
                AND sm.state = 'done'
                AND sm.location_id <> %s
                AND sm.location_dest_id = %s
                GROUP BY sm.product_id,
                pt.name,
                pp.default_code

                UNION ALL

                SELECT sm.product_id, pt.name, pp.default_code as code,
                    0 AS product_qty_in,
                    COALESCE(sum(sm.product_qty), 0) AS product_qty_out
                FROM stock_move sm
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day', COALESCE(sm.effective_date, sm.date)) < '%s'
                AND sm.state = 'done'
                AND sm.location_id = %s
                AND sm.location_dest_id <> %s
                GROUP BY sm.product_id,
                pt.name,
                pp.default_code) table_from GROUP BY product_id, name, code
        ''' % (date_start, location_outsource, location_outsource, date_start, location_outsource, location_outsource)

        sql_in = '''
            SELECT sm.product_id, pt.name, pp.default_code as code,
                    COALESCE(sum(sm.product_qty), 0) AS qty_in
                FROM stock_move sm 
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day', COALESCE(sm.effective_date, sm.date)) >= '%s'
                AND date_trunc('day', COALESCE(sm.effective_date, sm.date)) <= '%s'
                AND sm.state = 'done'
                AND sm.location_id <> %s
                AND sm.location_dest_id = %s
                GROUP BY sm.product_id,
                pt.name,
                pp.default_code
        '''% (date_start, date_end, location_outsource, location_outsource)

        sql_out = '''
            SELECT sm.product_id, pt.name, pp.default_code as code,
                    COALESCE(sum(sm.product_qty), 0) AS qty_out
                FROM stock_move sm 
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day', COALESCE(sm.effective_date, sm.date)) >= '%s'
                AND date_trunc('day', COALESCE(sm.effective_date, sm.date)) <= '%s'
                AND sm.state = 'done'
                AND sm.location_id = %s
                AND sm.location_dest_id <> %s
                GROUP BY sm.product_id,
                pt.name,
                pp.default_code
        '''% (date_start, date_end, location_outsource, location_outsource)

        sql_to = '''
            SELECT product_id,name, code, sum(product_qty_in - product_qty_out) as qty_to
                FROM  (SELECT sm.product_id, pt.name, pp.default_code as code,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_in,
                    0 AS product_qty_out
                FROM stock_move sm 
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day', COALESCE(sm.effective_date, sm.date)) <= '%s'
                AND sm.state = 'done'
                AND sm.location_id <> %s
                AND sm.location_dest_id = %s
                GROUP BY sm.product_id,
                pt.name,
                pp.default_code

                UNION ALL

                SELECT sm.product_id,pt.name, pp.default_code as code,
                    0 AS product_qty_in,
                    COALESCE(sum(sm.product_qty), 0) AS product_qty_out
                FROM stock_move sm 
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day', COALESCE(sm.effective_date, sm.date)) <= '%s'
                AND sm.state = 'done'
                AND sm.location_id = %s
                AND sm.location_dest_id <> %s
                GROUP BY sm.product_id,
                pt.name,
                pp.default_code) table_to GROUP BY product_id, name, code
        ''' % (date_end, location_outsource, location_outsource, date_end, location_outsource, location_outsource)

        sql = '''
            SELECT ROW_NUMBER() OVER(ORDER BY table_to.code DESC) AS num,
                    table_to.product_id, table_to.name, table_to.code,
                    COALESCE(sum(qty_from), 0) as qty_from,
                    COALESCE(sum(qty_in), 0) as qty_in,
                    COALESCE(sum(qty_out), 0) as qty_out,
                    COALESCE(sum(qty_to), 0) as qty_to
            FROM  (%s) table_to
                LEFT JOIN (%s) table_in on table_to.product_id = table_in.product_id
                LEFT JOIN (%s) table_out on table_to.product_id = table_out.product_id
                LEFT JOIN (%s) table_from on table_to.product_id = table_from.product_id
                GROUP BY table_to.product_id, table_to.name, table_to.code
        ''' %(sql_to, sql_in, sql_out, sql_from)
        self.env.cr.execute(sql)
        data = self.env.cr.dictfetchall()
        for i in data:
            list_product[i['num']] = {
                                    'name': i['name'],
                                    'code': i['code'],
                                    'qty_from': i['qty_from'],
                                    'qty_in': i['qty_in'],
                                    'qty_out': i['qty_out'],
                                    'qty_to': i['qty_to'],
                                 }
        return list_product
    
    @api.multi
    def create_xls_report(self):
        self.ensure_one()
        data = self._get_report_data()
        return {'type': 'ir.actions.report.xml',
                'report_name': 'inventory_report_between_dates_xls',
                'datas': data}
