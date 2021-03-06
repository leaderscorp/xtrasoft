# -*- coding: utf-8 -*-
from odoo import http
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception,content_disposition
import base64

class Binary(http.Controller):
 @http.route('/web/binary/download_document', type='http', auth="public")
 @serialize_exception
 def download_document(self,model,field,id,filename=None, **kw):
    """ Download link for files stored as binary fields.
    :param str model: name of the model to fetch the binary from
    :param str field: binary field
    :param str id: id of the record from which to fetch the binary
    :param str filename: field holding the file's name, if any
    :returns: :class:`werkzeug.wrappers.Response`
    """
    Model = request.registry[model]
    cr, uid, context = request.cr, request.uid, request.context
    fields = [field]
    res=request.env[model].search([('id','=',int(id))])
    filecontent = base64.b64decode(res.upload_sar or '')
    if not filecontent:
        return request.not_found()
    else:
        if not filename:
            filename = '%s_%s' % (model.replace('.', '_'), id)
        return request.make_response(filecontent,
                                [('Content-Type', 'application/octet-stream'),
                                 ('Content-Disposition', content_disposition(filename))])
class Report(http.Controller):
 @http.route('/web/report/download_report', type='http', auth="public")
 @serialize_exception
 def download_report(self,model,field,id,filename=None, **kw):
    """ Download link for files stored as binary fields.
    :param str model: name of the model to fetch the binary from
    :param str field: binary field
    :param str id: id of the record from which to fetch the binary
    :param str filename: field holding the file's name, if any
    :returns: :class:`werkzeug.wrappers.Response`
    """
    Model = request.registry[model]
    cr, uid, context = request.cr, request.uid, request.context
    fields = [field]
    res=request.env[model].search([('id','=',int(id))])
    filecontent = base64.b64decode(res.db_datas or '')
    if not filecontent:
        return request.not_found()
    else:
        if not filename:
            filename = '%s_%s' % (model.replace('.', '_'), id)
        return request.make_response(filecontent,
                                [('Content-Type', 'application/octet-stream'),
                                 ('Content-Disposition', content_disposition(filename))])

# class PecAcred(http.Controller):
#     @http.route('/pec_acred/pec_acred/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pec_acred/pec_acred/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pec_acred.listing', {
#             'root': '/pec_acred/pec_acred',
#             'objects': http.request.env['pec_acred.pec_acred'].search([]),
#         })

#     @http.route('/pec_acred/pec_acred/objects/<model("pec_acred.pec_acred"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pec_acred.object', {
#             'object': obj
#         })