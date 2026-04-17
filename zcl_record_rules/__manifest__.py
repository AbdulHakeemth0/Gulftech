# -*- coding: utf-8 -*-
{
    'name': "zcl record rules",
    'summary': """Record rules""",
    'description': """Record rules
    """,
    "version"      : "16.0.1.0.0",
    "author"       : "Zinfog Codelabs Pvt Ltd",
    "license"      : "LGPL-3",
    "website"      : "https://www.zinfog.com",
    'depends': ['base','stock','sale','account','purchase','zcl_quotations','zcl_pdc_management','zcl_purchase_requisition','zcl_invoice','zcl_cash_purcahse','zcl_cash_receipt','zcl_material_request'],
    'data': [
        'security/security.xml',
    ],
    "application": True,
    "installable": True,

}
