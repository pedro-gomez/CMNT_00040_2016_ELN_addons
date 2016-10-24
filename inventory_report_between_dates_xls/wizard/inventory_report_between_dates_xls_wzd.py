# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
        #cr = self.cr
        #uid = self.uid      
        result = []
        list_product = {}
        date_start = self.date_from
        date_end = self.date_to
        location_outsource = self.location_id.id
        sql_dk = '''
            SELECT product_id, name, code, sum(product_qty_in - product_qty_out) as qty_dk
                FROM (SELECT sm.product_id, pt.name, pp.default_code as code,
                    COALESCE(sum(sm.product_qty), 0) AS product_qty_in,
                    0 AS product_qty_out
                FROM stock_move sm
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day', sm.date) < '%s'
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
                WHERE date_trunc('day', sm.date) < '%s'
                AND sm.state = 'done'
                AND sm.location_id = %s
                AND sm.location_dest_id <> %s
                GROUP BY sm.product_id,
                pt.name,
                pp.default_code) table_dk GROUP BY product_id, name, code
        ''' % (date_start, location_outsource, location_outsource, date_start, location_outsource, location_outsource)

        sql_in_tk = '''
            SELECT sm.product_id, pt.name, pp.default_code as code,
                    COALESCE(sum(sm.product_qty), 0) AS qty_in_tk
                FROM stock_move sm 
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day', sm.date) >= '%s'
                AND date_trunc('day', sm.date) <= '%s'
                AND sm.state = 'done'
                AND sm.location_id <> %s
                AND sm.location_dest_id = %s
                GROUP BY sm.product_id,
                pt.name,
                pp.default_code
        '''% (date_start, date_end, location_outsource, location_outsource)

        sql_out_tk = '''
            SELECT sm.product_id, pt.name, pp.default_code as code,
                    COALESCE(sum(sm.product_qty), 0) AS qty_out_tk
                FROM stock_move sm 
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day', sm.date) >= '%s'
                AND date_trunc('day', sm.date) <= '%s'
                AND sm.state = 'done'
                AND sm.location_id = %s
                AND sm.location_dest_id <> %s
                GROUP BY sm.product_id,
                pt.name,
                pp.default_code
        '''% (date_start, date_end, location_outsource, location_outsource)

        sql_ck = '''
            SELECT product_id,name, code, sum(product_qty_in - product_qty_out) as qty_ck
                FROM  (SELECT sm.product_id, pt.name, pp.default_code as code,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_in,
                    0 AS product_qty_out
                FROM stock_move sm 
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day', sm.date) <= '%s'
                AND sm.state = 'done'
                AND sm.location_id <> %s
                AND sm.location_dest_id = %s
                GROUP BY sm.product_id,
                pt.name,
                pp.default_code

                UNION ALL

                SELECT sm.product_id,pt.name, pp.default_code as code,
                    0 AS product_qty_in,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_out

                FROM stock_move sm 
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day', sm.date) <= '%s'
                AND sm.state = 'done'
                AND sm.location_id = %s
                AND sm.location_dest_id <> %s
                GROUP BY sm.product_id,
                pt.name,
                pp.default_code) table_ck GROUP BY product_id, name, code
        ''' % (date_end, location_outsource, location_outsource, date_end, location_outsource, location_outsource)

        sql = '''
            SELECT ROW_NUMBER() OVER(ORDER BY table_ck.code DESC) AS num,
                    table_ck.product_id, table_ck.name, table_ck.code,
                    COALESCE(sum(qty_dk), 0) as qty_dk,
                    COALESCE(sum(qty_in_tk), 0) as qty_in_tk,
                    COALESCE(sum(qty_out_tk), 0) as qty_out_tk,
                    COALESCE(sum(qty_ck), 0) as qty_ck
            FROM  (%s) table_ck
                LEFT JOIN (%s) table_in_tk on table_ck.product_id = table_in_tk.product_id
                LEFT JOIN (%s) table_out_tk on table_ck.product_id = table_out_tk.product_id
                LEFT JOIN (%s) table_dk on table_ck.product_id = table_dk.product_id
                GROUP BY table_ck.product_id, table_ck.name, table_ck.code
        ''' %(sql_ck, sql_in_tk, sql_out_tk, sql_dk)
        self.env.cr.execute(sql)
        data = self.env.cr.dictfetchall()
        for i in data:
            #list_product.append({   'num': i['num'],
            #                        'name': i['name'],
            #                        'code': i['code'],
            #                        'qty_dk': i['qty_dk'],
            #                        'qty_in_tk': i['qty_in_tk'],
            #                        'qty_out_tk': i['qty_out_tk'],
            #                        'qty_ck': i['qty_ck'],
            #                     })
            list_product[i['num']] = {
                                    'name': i['name'],
                                    'code': i['code'],
                                    'qty_dk': i['qty_dk'],
                                    'qty_in_tk': i['qty_in_tk'],
                                    'qty_out_tk': i['qty_out_tk'],
                                    'qty_ck': i['qty_ck'],
                                 }
        return list_product
    
    @api.multi
    def create_xls_report(self):
        self.ensure_one()
        res = self._get_report_data()
        data = {}
        #for acc in res:
        #    data[acc.num] = res[acc]
        data = res
        return {'type': 'ir.actions.report.xml',
                'report_name': 'inventory_report_between_dates_xls',
                'datas': data}
