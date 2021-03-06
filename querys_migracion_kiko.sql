﻿
// CREAMOS UNA TABLA NUEVA PARA EVITAR RECURSIVIDAD

select * into aux_res_partner from res_partner;


//ACTUALIZAMOS LOS NOMBRES DE RES_PARTNER AL COMERCIAL DEL ADDRESS SI LO TIENE

update res_partner rp
set
name = new_name,
display_name = new_name,
phone = new_phone,
city = new_city
from
(
select rp.id,
case
	when not rpa.comercial isnull then rpa.comercial
	else (arp.name || ' / ' || rcs.name || ' (' || rp.zip || ')')
end as new_name,
rpa.city as new_city,
rpa.phone as new_phone
from res_partner rp
join res_country_state rcs on rcs.id = rp.state_id
join aux_res_partner arp on arp.id = rp.parent_id
join res_partner_address rpa on rpa.openupgrade_7_migrated_to_partner_id = rp.id
where not rp.parent_id isnull
)
as nt
where nt.id = rp.id


//ACTUALIZAMOS LOS DATOS DE EDI DE RES_PARTNER_ADDRESS A RES_PARTNER

update res_partner rp
set
gln_rf = nt.gln_rf, gln_rm = nt.gln_rm, gln_de = nt.gln_de, gln_co = nt.gln_co
from
(
select rpa.gln_rf, rp.id, rp.parent_id,
rpa.gln_rm, rpa.gln_de, rpa.gln_co
from res_partner rp
join res_country_state rcs on rcs.id = rp.state_id
join aux_res_partner arp on arp.id = rp.parent_id
join res_partner_address rpa on rpa.openupgrade_7_migrated_to_partner_id = rp.id
where not rp.parent_id isnull
)
as nt
where nt.id = rp.id and rp.gln_rf isnull


//DEBEMOS COMPROBAR SI ESTO ES NECESARIO: SI UN PARTNER NO TIENE EDI Y SU PARENT SI, SE ACTUALIZA AL DEL PARENT ??????
update res_partner rp
set
gln_rf = nt.gln_rf, gln_rm = nt.gln_rm, gln_de = nt.gln_de, gln_co = nt.gln_co
from aux_res_partner nt
where 
rp.parent_id = nt.id and
rp.gln_rf isnull and not rp.gln_rf isnull and
rp.gln_rm isnull and not rp.gln_rm isnull and
rp.gln_de isnull and not rp.gln_de isnull and
rp.gln_co isnull and not rp.gln_co isnull



//INSERTAR EN RES_PARTNER LOS DATOS DE RES_CONTACT (se pierde la relación con res_parnter pero no los datos, si no tiene nombre cogemos el nombre
del res_partner_address asociado?

insert into res_partner 
(create_uid, write_uid, lang, use_parent_address, type, customer, employee, supplier, agent, opt_out, vat_subjected, color, 
is_company, active, user_id, agent_type, settlement,contact_type, notify_email, display_name, name, phone, mobile, fax, email, gln_de, gln_rf, gln_rm, gln_co, 
parent_id, company_id, street, street2, zip, title, state_id, city, country_id)
(
select 1,1,'es ES', false, 'contact', false, false, false, false,  false, false, 0 as color, 
false as is_company, true as active, 1 as user_id, 'agent' as agent_type, 'monthly' as settlement, 'standalone' as contact_type, 'always' as notify_email, 
case
    when rpc.last_name = '/' then 'CONTACTO DE ' || coalesce(rpa.comercial, rpa.name, rp.comercial, rp.name)
    else coalesce(rpc.first_name, '') || '_' || coalesce(rpc.last_name, '')
end as display_name,
case
    when rpc.last_name = '/' then 'CONTACTO DE ' || coalesce(rpa.comercial, rpa.name, rp.comercial, rp.name)
    else coalesce(rpc.first_name, '') || '_' || coalesce(rpc.last_name, '')
end as name,
rpa.phone as phone, rpc.mobile as mobile, rpa.fax as fax, rpc.email || ',' || rpa.email as email,
rpa.gln_de as gln_de, rpa.gln_rf as gln_rf, rpa.gln_rm as gln_rm, rpa.gln_co as gln_co,
rpa.openupgrade_7_migrated_to_partner_id as parent_id,
rpa.company_id as company_id,
rpa.street as street, rpa.street2 as street2, rpa.zip as zip, rpa.title as title, rpa.state_id as state_id, rpa.city as city, rpa.country_id as country_id
from res_partner_contact rpc
inner join res_partner_address rpa on rpa.contact_id = rpc.id
inner join res_partner rp  on rpa.openupgrade_7_migrated_to_partner_id = rp.id);


//BORRAMOS LA TABLA AUXILIAR

drop table if exists aux_res_partner

//PRODUCCION

//STOCK_MOVE TIENE UN MANY2ONE A MRP_PRODUCTION, HEREDADO DE UN MANY TO MANY Y HAY QUE ACTUALIZAR YA QUE NO SE HA MIGRADO ?

update stock_move set raw_material_production_id = (select production_id from mrp_production_move_ids where move_id = stock_move.id)
where raw_material_production_id isnull

// LOS PRODUCTOS DEL NOGAL DEBEN DE ESTAR ESTABLECIDOS A company_id = False
// el nogal company_id = 1

update product_template set company_id = null where company_id = 1


//FALLO DE SEGURIDAD DEBIDO AL ARBOL DE ALMACENES

update stock_warehouse set view_location_id = 151 where id = 4
update stock_warehouse set view_location_id = 150 where id = 6