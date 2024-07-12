from odoo import models, fields, api, _
from odoo.addons.is_dynacase2odoo.models.is_param_project import TYPE_DOCUMENT
from datetime import datetime, timedelta
import calendar
from random import *
import base64
import cairo
from PIL import Image
import time
import os
from matplotlib.colors import to_rgb
import codecs


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
            titre="?"
            if obj.type_document=="Moule":
                domain=[
                    ('idmoule','=',obj.moule_id.id)
                ]
                titre="%s - %s"%(obj.moule_id.name,obj.moule_id.designation)
            if obj.type_document=="dossier_appel_offre":
                domain=[
                    ('dossier_appel_offre_id','=',obj.dossier_appel_offre_id.id)
                ]
                titre=obj.dossier_appel_offre_id.dao_num
            if obj.type_document=="Dossier Modif Variante":
                domain=[
                    ('dossier_modif_variante_id','=',obj.dossier_modif_variante_id.id)
                ]
                titre=obj.dossier_modif_variante_id.demao_num
            if domain==[]:
                return
            res=self.env['is.doc.moule'].get_dhtmlx(domain=domain)
            items = res['items']
            #******************************************************************

            #** Calcul start_date *********************************************
            for item in items:
                end_date = item.get('end_date')
                duration =  item.get('duration')
                if end_date and  duration:
                    end_date   = datetime.strptime(end_date, '%Y-%m-%d 00:00:00')
                    start_date = end_date - timedelta(days=duration)
                    item['start_date'] = start_date
                    item['end_date']   = end_date
                    #print("id=%s : end_date=%s : duration=%s : start_date=%s"%(item['id'],item.get('end_date'),item.get('duration'),start_date))
            #******************************************************************

            #** Recherche des enfants de chaque niveau ************************
            def get_enfants(items,parent,niveau):
                "Recherche des enfants du parent indiqué"
                for item in items:
                    if item.get('parent')==parent:
                        item['niveau'] = niveau
                        enfants.append(item)
                        get_enfants(items, item['id'], niveau+1)
                return
            enfants=[]
            get_enfants(items,False,0)
            #******************************************************************
 
            #** Calcul date de debut et de fin des parents ********************
            fin=False
            while fin==False:
                fin=True
                for enfant in enfants:
                    end_date = enfant.get('end_date')
                    if end_date:
                        for enfant2 in enfants:
                            if enfant2['id']==enfant.get('parent'):
                                if 'end_date' not in enfant2:
                                    enfant2['end_date']=end_date
                                    fin=False
                                if enfant2['end_date']<end_date:
                                    enfant2['end_date']=end_date
                                    fin=False
                    start_date = enfant.get('start_date')
                    if start_date:
                        for enfant2 in enfants:
                            if enfant2['id']==enfant.get('parent'):
                                if 'start_date' not in enfant2 or enfant2['start_date']==False:
                                    enfant2['start_date']=start_date
                                    fin=False
                                if enfant2['start_date']>start_date:
                                    enfant2['start_date']=start_date
                                    fin=False
            #******************************************************************

            #** Ajout des durations pour les parents **************************
            for enfant in enfants:
                if 'duration' not in enfant or enfant['duration']==False:
                    enfant['duration'] = (enfant['end_date'] - enfant['start_date']).days
            #******************************************************************

            #** Ajout de la couleur de la section **************************
            for enfant in enfants:
                model  = enfant.get('model')
                res_id = int(enfant.get('res_id') or 0)
                color = "#1b81e8"
                o = self.env[model].browse(res_id)
                if o:
                    if model=='is.doc.moule' and o.section_id:
                        color = o.section_id.color
                    if model=='is.section.gantt':
                        color = o.color
                enfant['color'] = color
            #******************************************************************

            #** Resultat ******************************************************            
            #for enfant in enfants:
            #    print(enfant)
            #   #print(enfant['niveau'],enfant['id'],enfant.get('start_date'),enfant.get('duration'),enfant.get('end_date'))
            #******************************************************************


            #** Recherche du nombre de jours **********************************
            def get_date(end_date,duration):
                start_date = False
                if end_date:
                    start_date = end_date - timedelta(days=duration)
                    #start_date = datetime.strptime(end_date, '%Y-%m-%d 00:00:00') - timedelta(days=duration)
                return start_date
            date_debut = date_fin = False
            items = enfants
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
                    ctx.set_line_width(0.2) 
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
            cairo_show_text(ctx,110,entete_height,font_size=24,txt=titre)



            #** Entete du tableau *********************************************
            cairo_rectangle(ctx,0,entete_height,WIDTH,tache_height,line_rgb=(0.8, 0.8, 0.8))
            #cairo_rectangle(ctx,0,entete_height+tache_height,WIDTH,tache_height,line_rgb=(0.8, 0.8, 0.8))

            #** Mois **********************************************************
            ladate = date_debut
            lesmois=[]
            for x in range(0,int(jour_nb)):
                txt = ladate.strftime("%m/%Y")
                if x==0 or ladate.day==1:
                    cemois=calendar.monthrange(ladate.year,ladate.month)
                    premier_du_mois=ladate.day
                    dernier_du_mois=cemois[1]
                    fin_mois = ladate + timedelta(days=dernier_du_mois)
                    delta = (fin_mois - date_fin).days
                    if delta>0:
                        dernier_du_mois = dernier_du_mois - delta
                    lesmois.append((txt,premier_du_mois,dernier_du_mois))
                ladate += timedelta(days=1)
            decal=0
            for mois in lesmois:
                nb_jours_mois = mois[2]-mois[1]+1 #dernier_du_mois - premier_du_mois
                x      = grille_width+decal*jour_width
                y      = entete_height
                width  = nb_jours_mois *  jour_width
                height = tache_height
                cairo_rectangle(ctx,x,y,width,height,line_rgb=(0.8, 0.8, 0.8))
                cairo_show_text(ctx,x+2,y+tache_height,txt=mois[0])
                decal+=nb_jours_mois

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
                    fill_rgb=to_rgb("#fadcb8")
                    cairo_rectangle(ctx,grille_width+x*jour_width,entete_height+tache_height*1,jour_width,(jour_nb+1)*tache_height,fill_rgb=fill_rgb)
                ladate += timedelta(days=1)

            #** Création des rectangles des lignes pour les tâches ************
            y=0
            for item in items:
                #if item.get('model')=='is.doc.moule':
                cairo_rectangle(ctx,0,entete_height + entete_table_height + y*tache_height,grille_width,tache_height,line_rgb=(0.8, 0.8, 0.8))
                txt = '%s %s'%('- '*item.get('niveau'),item.get('text'))
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
                fill_rgb = to_rgb(item.get('color'))
                cairo_rectangle(ctx,decal*jour_width+grille_width, entete_height + entete_table_height + y*tache_height+3 ,duration*jour_width,tache_height-6,fill_rgb=fill_rgb)
                y+=1


            #Ajouter le logo sauf pour le SVG ou cela ne fonctionne pas ***********
            if file_extension!="svg":
                #** Convertir la surface au format PIL pour ajouter le logo *******
                def surface_to_pil(surface: cairo.ImageSurface) -> Image:
                    format = surface.get_format()
                    size = (surface.get_width(), surface.get_height())
                    stride = surface.get_stride()
                    with surface.get_data() as memory:
                        if format == cairo.Format.RGB24:
                            return Image.frombuffer(
                                "RGB", size, memory.tobytes(),
                                'raw', "BGRX", stride)
                        elif format == cairo.Format.ARGB32:
                            return Image.frombuffer(
                                "RGBA", size, memory.tobytes(),
                                'raw', "BGRa", stride)
                        else:
                            raise NotImplementedError(repr(format))

                def pil_to_surface(image):
                    return cairo.ImageSurface.create_for_data(
                        bytearray(image.tobytes('raw', 'BGRa')),
                        cairo.FORMAT_ARGB32,
                        image.width,
                        image.height,
                        )

                #** Logo au format PIL et redimmensionnement **********************
                logo_path="/tmp/logo-gantt-pdf.png"
                company = self.env.user.company_id
                f = open(logo_path,'wb')
                f.write(base64.b64decode(company.logo))
                f.close()
                image_logo = Image.open(logo_path)  
                width, height = image_logo.size 
                max_height = entete_height
                ratio = height/max_height
                new_width = int(width/ratio)
                image_logo_resize = image_logo.resize((new_width, max_height))

                #** Combiner le logo et le gantt **********************************
                result_pil = Image.new(
                    mode = 'RGBA',
                    size = (surface.get_width(), surface.get_height()),
                    color = (0, 0, 0, 0),
                    )
                surface_pil = surface_to_pil(surface) # Convertir le Gantt au format 'surface' au format PIL
                result_pil.paste(surface_pil)         # Ajout du Gantt au format PIL
                result_pil.paste(image_logo_resize)   # Ajout du logo au format PIL
                surface = pil_to_surface(result_pil)  # Convertir le format PIL en format 'surface'


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


