from odoo import models, fields, api, _
from odoo.addons.is_dynacase2odoo.models.is_param_project import TYPE_DOCUMENT
from datetime import datetime, timedelta
from random import *
import base64
import cairo
import time
import os


class IsGanttPdf(models.Model):
    _name        = "is.gantt.pdf"
    _inherit=['mail.thread']
    _description = "PDF du Gantt"
    _order = "name"


    name                      = fields.Char("Document", compute='_compute_name',store=True, readonly=True)
    type_document             = fields.Selection(TYPE_DOCUMENT,string="Type de document", default="Moule", required=True)
    moule_id                  = fields.Many2one("is.mold"                  , string="Moule")
    dossierf_id               = fields.Many2one("is.dossierf"              , string="Dossier F")
    dossier_modif_variante_id = fields.Many2one("is.dossier.modif.variante", string="Dossier Modif / Variante")
    dossier_article_id        = fields.Many2one("is.dossier.article"       , string="Dossier article")
    dossier_appel_offre_id    = fields.Many2one("is.dossier.appel.offre"   , string="Dossier appel d'offre")
    date_debut                = fields.Date("Date début")
    date_fin                  = fields.Date("Date fin")
    format_fichier           = fields.Selection([
        ("png", "PNG"),
        ("pdf", "PDF"),
        ("svg", "SVG"),
    ], string="Format fichier", default="png")


    @api.depends('type_document', 'moule_id', 'dossierf_id', 'dossier_modif_variante_id', 'dossier_article_id', 'dossier_appel_offre_id')
    def _compute_name(self):
        for obj in self:
            name=""
            if obj.type_document=="Moule":
                name = obj.moule_id.name
            if obj.type_document=="Dossier F":
                name = obj.dossierf_id.name
            if obj.type_document=="Article":
                name = obj.dossier_article_id.code_pg
            if obj.type_document=="Dossier Modif Variante":
                name = obj.dossier_modif_variante_id.demao_num
            if obj.type_document=="dossier_appel_offre":
                name = obj.dossier_appel_offre_id.dao_num
            obj.name = name


    def generer_pdf_action(self):
        for obj in self:
            #** Recherche des tâches ******************************************
            domain=[]
            if obj.type_document=="Moule":
                domain=[
                    ('idmoule','=',obj.moule_id.id)
                ]
            if obj.type_document=="dossier_appel_offre":
                domain=[
                    ('dossier_appel_offre_id','=',obj.dossier_appel_offre_id.id)
                ]
            if obj.type_document=="Dossier Modif Variante":
                domain=[
                    ('dossier_modif_variante_id','=',obj.dossier_modif_variante_id.id)
                ]
            if domain==[]:
                return
            res=self.env['is.doc.moule'].get_dhtmlx(domain=domain)
            items = res['items']
            #******************************************************************

            # {'id': 'is.doc.moule-106837', 'model': 'is.doc.moule', 'res_id': 106837, 'text': 'tata (Autre)', 'end_date': '2024-06-18 00:00:00"', 'duration': 1, 'parent': 50019539, 'priority': 0, 'color_class': 'etat_a_faire is_param_projet_189', 'section': 'Section 2', 'responsable': 'Administrator', 'j_prevue': '?'}

            #** Recherche du nombre de jours **********************************
            def get_date(end_date,duration):
                start_date = False
                if end_date:
                    start_date = datetime.strptime(end_date, '%Y-%m-%d 00:00:00') - timedelta(days=duration)
                return start_date
            date_debut = date_fin = False
            for item in items:
                duration   = item.get('duration')
                end_date   = get_date(item.get('end_date'),0)
                start_date = get_date(item.get('end_date'),duration)
                if start_date:
                    if not date_debut or date_debut>start_date:
                        date_debut =start_date
                if end_date:
                    if not date_fin or date_fin<end_date:
                        date_fin = end_date
            delta = (date_fin-date_debut).days
            #******************************************************************

            #** Paramètres du Gannt *******************************************
            file_extension = obj.format_fichier  # svg, png ou pdf
            file_name = obj.name
            file_name_with_extension = "%s.%s"%(file_name,file_extension)
            path = "/tmp/%s"%file_name_with_extension 

            tache_nb            = len(items)
            tache_height        = 20
            jour_nb             = delta
            jour_width          = 13
            grille_width        = 30*jour_width
            entete_height       = 2*tache_height # Entête pour placer le logo et un titre (ex : le moule)
            entete_table_height = 2*tache_height # Entête du tableau pour mettre les jours et les semaines

            WIDTH = grille_width + jour_nb*jour_width
            HEIGHT = entete_height + entete_table_height + tache_nb*tache_height
            #******************************************************************


            if file_extension=="svg":
                surface = cairo.SVGSurface(path, WIDTH, HEIGHT)
            else:
                surface = cairo.ImageSurface(cairo.FORMAT_RGB24,WIDTH,HEIGHT)
            ctx = cairo.Context(surface)


            def cairo_rectangle(ctx,x,y,width,height,line_width=1,line_rgb=False,fill_rgb=False):
                ctx.rectangle(x, y, width, height)
                if fill_rgb:
                    ctx.set_source_rgb(fill_rgb[0],fill_rgb[1],fill_rgb[2])
                    ctx.fill()
                if line_rgb:
                    ctx.set_source_rgb(line_rgb[0],line_rgb[1],line_rgb[2])
                    ctx.set_line_width(1) 
                    ctx.stroke() 
                

            def cairo_show_text(ctx,x,y,font_rgb=(0,0,0),font_size=12,txt=""):
                txt=txt or ''
                ctx.set_source_rgb(font_rgb[0],font_rgb[1],font_rgb[2])
                ctx.set_font_size(font_size)
                ctx.select_font_face("Arial",cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_NORMAL)
                xbearing, ybearing, txt_width, txt_height, dx, dy = ctx.text_extents(txt)
                ctx.move_to(x, y-txt_height/2)
                ctx.show_text(txt)


            #** Fond gris clair pour toute la surface *************************
            cairo_rectangle(ctx,0,0,WIDTH,HEIGHT,fill_rgb=(0.95, 0.95, 0.95))

            #** Entete du Gantt ***********************************************
            cairo_rectangle(ctx,0,0,WIDTH,entete_height,line_rgb=(0.8, 0.8, 0.8))

            #** Entete du tableau *********************************************
            cairo_rectangle(ctx,0,entete_height,WIDTH,tache_height,line_rgb=(0.8, 0.8, 0.8))
            cairo_rectangle(ctx,0,entete_height+tache_height,WIDTH,tache_height,line_rgb=(0.8, 0.8, 0.8))

            #** Semaines ******************************************************
            ladate = date_debut
            for x in range(0,int(jour_nb/7)):
                cairo_rectangle(ctx,grille_width+x*jour_width*7,entete_height+tache_height,jour_width*7,tache_height,line_rgb=(0.8, 0.8, 0.8))
                txt = ladate.strftime("S%W")
                cairo_show_text(ctx,grille_width+x*jour_width*7+2,entete_height + entete_table_height-1,txt=txt)
                ladate += timedelta(days=7)
            
            #** weekend en couleur ********************************************
            ladate = date_debut
            for x in range(0,jour_nb):
                if ladate.weekday() in (5,6):
                    cairo_rectangle(ctx,grille_width+x*jour_width,entete_height+tache_height*2,jour_width,jour_nb*tache_height,fill_rgb=(0.7, 0.7, 0.7))
                ladate += timedelta(days=1)

            #** Création des rectangles des lignes pour les tâches ************
            y=0
            for item in items:
                #if item.get('model')=='is.doc.moule':
                cairo_rectangle(ctx,0,entete_height + entete_table_height + y*tache_height,grille_width,tache_height,line_rgb=(0.8, 0.8, 0.8))
                txt = item.get('text')
                cairo_show_text(ctx,5,entete_height + entete_table_height + (y+1)*tache_height-1,txt=txt)
                for x in range(0,jour_nb):
                    cairo_rectangle(ctx,x*jour_width+grille_width,entete_height + entete_table_height + y*tache_height,jour_width,tache_height,line_rgb=(0.8, 0.8, 0.8))
                y+=1

            #** Ajout des tâches **********************************************
            y=0
            for item in items:
                duration   = item.get('duration')
                end_date   = get_date(item.get('end_date'),0)
                start_date = get_date(item.get('end_date'),duration)
                decal = 0
                if start_date:
                    decal = (start_date - date_debut).days
                fill_rgb=(random(),random(),random())
                cairo_rectangle(ctx,decal*jour_width+grille_width,entete_height + entete_table_height + y*tache_height,duration*jour_width,tache_height,fill_rgb=fill_rgb)
                y+=1

            #** Enregistrement du fichier ************************************* 
            if file_extension=="png":
                surface.write_to_png(path) # 2380 × 1684 pixels
                ctx.show_page()
                surface.finish()
                surface.flush()


            if file_extension=="pdf":
                # A4 portrait (point) : 595  , 842
                # A3 paysage (point)  : 595*2, 842
                # A2 portrait (point) : 595*2, 842*2
                # A1 paysage (point)  : 595*4, 842*2 (840 × 594 mm)
                pdf_surface = cairo.PDFSurface(path, WIDTH, HEIGHT) # 1 point = 0.3527777778 mm => https://www.unitconverters.net/length/point-to-millimeter.htm
                pdf_context = cairo.Context(pdf_surface)
                pdf_context.set_source_surface(surface)
                pdf_context.paint()
                pdf_context.show_page()
                pdf_surface.finish()
                pdf_surface.flush()



            if file_extension=="svg":
                surface.finish()
                surface.flush()

            # ** Creation ou modification de la pièce jointe ******************
            attachment_obj = self.env['ir.attachment']
            attachments = attachment_obj.search([('res_id','=',obj.id),('name','=',file_name_with_extension)])
            datas = open(path,'rb').read()
            vals = {
                'name':        file_name_with_extension,
                'type':        'binary',
                'res_model':   self._name,
                'res_id':      obj.id,
                'datas':       base64.b64encode(datas),
            }
            if attachments:
                attachments.unlink()

            #attach = Attachment.with_context(image_no_postprocess=True).create({
            attachment_obj.with_context(image_no_postprocess=True).create(vals)
            os.unlink(path)
            #*******************************************************************


