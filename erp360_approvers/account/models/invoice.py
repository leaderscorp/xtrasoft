# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo import tools
from lxml import etree
from odoo.tools.safe_eval import safe_eval
from ... import generic as gen
from num2words import num2words

class document_approver(models.Model):
    _name = "document.approver"
    _order = 'sequence'
    _description ="Manage Document Approvers"
    
    
    @api.onchange('system_user')
    def onchange_system_user(self):
        self.user_id = ''
        self.name = ''
    
    @api.depends('user_id','user2_id')
    def _get_name(self):
        for x in self:
            name = ''
            if x.user_id:
                name = x.user_id.name
            if x.user2_id:
                name = x.user2_id.name
            x.name = name
    
    def _set_name(self):
        pass
    
    name = fields.Char(string="User", compute=_get_name, inverse=_set_name, store=True)
    system_user = fields.Boolean(string="Is System User", default=True)
    sequence = fields.Integer(string="Sequence")
    user_id = fields.Many2one('res.users', string="Approver")
    authority = fields.Char(string="Approved As")
    user2_id = fields.Many2one('res.users',string="Delegated User", relation="res.users")
    authority2 = fields.Char(string="Approved As")
    document_type = fields.Selection(gen.DocumentTypes, string="Document Type")
    action_taken_as = fields.Char(string="Action Taken as")


class document_approver_detail(models.Model):
    _name = "document.approver.detail"
    _order = 'sequence'
    _description ="Manage Document Approvers Detail"
    
    name = fields.Char(string="User")
    sequence = fields.Integer(string="Sequence")
    model = fields.Char(string="Model")
    res_id = fields.Integer(string="Record")
    document_type = fields.Char(string="Document Type")
    user_id = fields.Many2one('res.users', string="Approver")
    authority = fields.Char(string="Approved As") 
    action = fields.Selection([('Accept','Accept'),('Reject','Reject')], string="Action")
    date = fields.Datetime(string="Approved Date")
    comment = fields.Text(string="Comment")
    move_id = fields.Many2one('account.move', ondelete='cascade')
    expense_sheet_id = fields.Many2one('hr.expense.sheet', ondelete='cascade')
    image_128 = fields.Binary(related="user_id.image_128", readonly=False, relation="res.users")
    previous_approval = fields.Many2one('document.approver.detail')
    valid_user = fields.Integer(compute="_check_validity", default=0)
    action_taken_as = fields.Char(string="Action Taken as")
    
    def _check_validity(self):
        for x in self:
            valid = 0
            if x.user_id.id == x.env.user.id:
                if x.previous_approval:
                    if x.previous_approval.action == 'Accept' and x.action not in ('Accept','Reject'):
                        valid = 1
                else:
                    if x.action in ('Accept','Reject'):
                        valid = 0
                    else:
                        valid = 1
            x.valid_user = valid
    
    def accept(self):
        self.write({'action': 'Accept','date':fields.Datetime.now()})
    
    
    def reject(self):
        self.write({'action': 'Reject','date':fields.Datetime.now()})
        
class account_move(models.Model):
    _inherit = "account.move"
    
    
    def button_draft(self):
        if self.approver_ids:
            self.approver_ids.write({'action':''})
        else:
            self.approver_ids = self._get_approvers()
        res = super(account_move, self).button_draft()
        return res
        
        
    def action_post(self):
        if self.approver_ids:
            rec = self.approver_ids.filtered(lambda x: x.action == 'Accept')
            if len(rec) != len(self.approver_ids):
                raise ValidationError("Approval process is not completed")
            
#         inv_type = self._context.get('default_type',False)
#         document_type = None
#         if inv_type == 'in_invoice':
#             document_type = 'Vendor Bill'
#         if inv_type == 'entry':
#             document_type = 'Journal Entries'
#         if document_type:
#             rec = self.approver_ids.filtered(lambda x: x.document_type == document_type)
#             rec1 = self.approver_ids.filtered(lambda x: x.document_type == document_type and x.action == 'Accept')
#             if len(rec1) != len(rec):
#                 raise ValidationError("Approval process is not completed")
        
        return super(account_move, self).action_post()
        
    def adjust_approval_seq(self):
        previous = ''
        current = ''
        for x in self.approver_ids:
            if x.user_id:
                if current:
                    previous = current
                current = x.id 
                if previous:
                    x.previous_approval = previous 
            
    
    
    @api.model
    def create(self, vals):
        res = super(account_move, self).create(vals)
        if vals.get('approver_ids',False):
            res.adjust_approval_seq()
        return res
    
    def _get_approvers(self):
        data = []
        result = None
        inv_type = self._context.get('default_type',False)
        document_type = None
        if inv_type == 'in_invoice':
            document_type = 'Vendor Bill'
            result = self.env['document.approver'].search([('document_type','=',document_type)], order="sequence")
        if inv_type == 'entry':
            document_type = 'Journal Entries'
            result = self.env['document.approver'].search([('document_type','=',document_type)], order="sequence")
        if result:
            for x in result:
                user_id = False
                authority = ''
                if x.user2_id:
                    user_id = x.user2_id.id or ''
                    authority = x.authority2 or ''
                else:
                    user_id = x.user_id.id or ''
                    authority = x.authority or ''
                
                data.append((0,0,dict(
                    name = x.name,
                    sequence = x.sequence,
                    document_type = document_type,
                    user_id= user_id, 
                    authority = authority,
                    action_taken_as = x.action_taken_as
                    )))
            
        return data
        
    
    approver_ids = fields.One2many('document.approver.detail', 'move_id', default=_get_approvers)
        
    
    
class hr_expense_sheet(models.Model):
    _inherit = "hr.expense.sheet"
    amount_in_words = fields.Char(string="Amount in Words",compute="cal_amount_in_words",store=True)
    
    @api.depends('total_amount', 'currency_id')
    def cal_amount_in_words(self):
        for each in self:
            each.amount_in_words = each.currency_id.amount_to_text(each.total_amount) if each.currency_id else ''
    def action_sheet_move_create(self):
        
        document_type = 'Expenses'
        if document_type:
            rec = self.approver_ids.filtered(lambda x: x.document_type == document_type)
            rec1 = self.approver_ids.filtered(lambda x: x.document_type == document_type and x.action == 'Accept')
            if len(rec1) != len(rec):
                raise ValidationError("Approval process is not completed")
        
        return super(hr_expense_sheet, self).action_sheet_move_create()
        
    def adjust_approval_seq(self):
        previous = ''
        current = ''
        for x in self.approver_ids:
            if x.user_id:
                if current:
                    previous = current
                current = x.id 
                if previous:
                    x.previous_approval = previous 
            
    
    
    def write(self, vals):
        res = super(hr_expense_sheet, self).write(vals)
        if vals.get('account_move_id',False):
            self.env.cr.execute("update document_approver_detail set move_id = %s where expense_sheet_id = %s"%(vals['account_move_id'],self.id,))
        return res
        
    
    @api.model
    def create(self, vals):
        res = super(hr_expense_sheet, self).create(vals)
        if vals.get('approver_ids',False):
            res.adjust_approval_seq()
        return res
    
    def _get_approvers(self):
        data = []
        document_type = "Expenses"
        result = self.env['document.approver'].search([('document_type','=',document_type)], order="sequence")
        if result:
            for x in result:
                user_id = False
                authority = ''
                if x.user2_id:
                    user_id = x.user2_id.id or ''
                    authority = x.authority2 or ''
                else:
                    user_id = x.user_id.id or ''
                    authority = x.authority or ''
                
                data.append((0,0,dict(
                    sequence = x.sequence,
                    document_type = document_type,
                    user_id= user_id, 
                    authority = authority,
                    name = x.name,
                    action_taken_as = x.action_taken_as
                    )))
            
        return data
        
    
    approver_ids = fields.One2many('document.approver.detail', 'expense_sheet_id', default=_get_approvers)    
    
class ReportInvoiceWithPayment(models.AbstractModel):
    _inherit = 'report.account.report_invoice_with_payments'
    _description = 'Account report with payment lines'

    @api.model
    def _get_report_values(self, docids, data=None):
        approver_obj=self.env['document.approver.detail'].search([('move_id','=',docids)])
        account_move=self.env['account.move'].browse(docids)
        amount_in_words=""
        if account_move:
            rupees = num2words(account_move.amount_total, to='cardinal', lang='en_IN')
            amount_in_words = str(rupees).title()
            amount_in_words=amount_in_words.replace("-", ' ')+" Rupees Only."
              
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': self.env['account.move'].browse(docids),
            'approver_obj':approver_obj,
            'report_type': data.get('report_type') if data else '',
            'amount_in_words':amount_in_words
        }
   
