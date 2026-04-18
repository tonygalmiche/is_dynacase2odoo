-- 1. Supprimer les données
DROP TABLE IF EXISTS is_demande_consultation_line_fournisseur CASCADE;
DROP TABLE IF EXISTS is_demande_consultation_line CASCADE;
DROP TABLE IF EXISTS is_demande_consultation CASCADE;

-- 2. Supprimer les vues UI
DELETE FROM ir_ui_view
WHERE model IN (
    'is.demande.consultation',
    'is.demande.consultation.line',
    'is.demande.consultation.line.fournisseur'
);

-- 3. Supprimer les actions fenêtre
DELETE FROM ir_act_window
WHERE res_model IN (
    'is.demande.consultation',
    'is.demande.consultation.line',
    'is.demande.consultation.line.fournisseur'
);

-- 4. Nettoyer ir_model_data
DELETE FROM ir_model_data 
WHERE name LIKE '%is_demande_consultation%';

-- 5. Nettoyer les sélections de champs
DELETE FROM ir_model_fields_selection 
WHERE field_id IN (
    SELECT id FROM ir_model_fields 
    WHERE model IN (
        'is.demande.consultation',
        'is.demande.consultation.line',
        'is.demande.consultation.line.fournisseur'
    )
);

-- 6. Nettoyer les champs
DELETE FROM ir_model_fields 
WHERE model IN (
    'is.demande.consultation',
    'is.demande.consultation.line',
    'is.demande.consultation.line.fournisseur'
);

-- 7. Nettoyer les accès et règles
DELETE FROM ir_model_access 
WHERE model_id IN (
    SELECT id FROM ir_model WHERE model IN (
        'is.demande.consultation',
        'is.demande.consultation.line',
        'is.demande.consultation.line.fournisseur'
    )
);

DELETE FROM ir_rule 
WHERE model_id IN (
    SELECT id FROM ir_model WHERE model IN (
        'is.demande.consultation',
        'is.demande.consultation.line',
        'is.demande.consultation.line.fournisseur'
    )
);

-- 8. Supprimer les modèles
DELETE FROM ir_model 
WHERE model IN (
    'is.demande.consultation',
    'is.demande.consultation.line',
    'is.demande.consultation.line.fournisseur'
);






-- Nouvelles vues pour THEIA pour éviter le 
-- 2026-04-17 06:24:10,445 1843 INFO pg-odoo16-3 odoo.modules.loading: loading is_plastigray16/views/is_theia_view.xml 
-- 2026-04-17 06:24:11,063 1843 INFO pg-odoo16-3 odoo.models.unlink: User #1 deleted ir.actions.act_window.view records with IDs: [2133, 2134] 
DELETE FROM ir_act_window_view 
WHERE act_window_id = (
    SELECT res_id FROM ir_model_data 
    WHERE module = 'is_plastigray16' 
    AND name = 'is_theia_dequalification_moule_action'
);

-- Supprimer les ir.actions.act_window.view orphelins de is_theia_presse_action (is_equipement_view.xml)
-- 2026-04-17 06:33:57,296 1988 INFO pg-odoo16-1 odoo.modules.loading: loading is_plastigray16/views/is_equipement_view.xml 
-- 2026-04-17 06:33:57,547 1988 INFO pg-odoo16-1 odoo.models.unlink: User #1 deleted ir.actions.act_window.view records with IDs: [8275, 8276] 
DELETE FROM ir_act_window_view
WHERE act_window_id = (
    SELECT res_id FROM ir_model_data
    WHERE module = 'is_plastigray16'
    AND name = 'is_theia_presse_action'
);

-- Supprimer les ir.actions.act_window.view orphelins de is_questionnaire_dms_view.xml
-- 2026-04-17 06:39:51,157 INFO odoo.models.unlink: deleted ir.actions.act_window.view records with IDs: [8317, 8318]
-- 2026-04-17 06:39:51,171 INFO odoo.models.unlink: deleted ir.actions.act_window.view records with IDs: [8319, 8320]
DELETE FROM ir_act_window_view
WHERE act_window_id = (
    SELECT res_id FROM ir_model_data
    WHERE module = 'is_plastigray16'
    AND name = 'is_questionnaire_dms_questionnaire_action'
);
DELETE FROM ir_act_window_view
WHERE act_window_id = (
    SELECT res_id FROM ir_model_data
    WHERE module = 'is_plastigray16'
    AND name = 'is_questionnaire_dms_reponse_action'
);

-- Supprimer les ir.actions.act_window.view orphelins de is_stock_production_lot_action (stock_view.xml)
-- 2026-04-17 06:43:28,042 INFO odoo.models.unlink: deleted ir.actions.act_window.view records with IDs: [8331, 8332]
DELETE FROM ir_act_window_view
WHERE act_window_id = (
    SELECT res_id FROM ir_model_data
    WHERE module = 'is_plastigray16'
    AND name = 'is_stock_production_lot_action'
);

-- Supprimer les ir.actions.act_window.view orphelins de action_ir_filters_personal (ir_filters_view.xml)
-- 2026-04-17 09:37:03,804 1434 INFO pg-odoo16-1 odoo.models.unlink: User #1 deleted ir.actions.act_window.view records with IDs: [8357, 8358]
DELETE FROM ir_act_window_view
WHERE act_window_id = (
    SELECT res_id FROM ir_model_data
    WHERE module = 'is_plastigray16'
    AND name = 'action_ir_filters_personal'
);

