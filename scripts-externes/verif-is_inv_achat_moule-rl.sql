-- Objectif :
-- Suite à des copies de "Revue de lancement" (is.revue.lancement), les champs
-- rl_be01_id à rl_be17_id (liens vers is.inv.achat.moule) ont été copiés alors
-- qu'ils ne l'auraient pas dû (correction copy=False depuis). Ces liens pointent
-- donc encore vers des is.inv.achat.moule dont le moule / dossier F correspond à
-- la revue de lancement d'origine, et non à la nouvelle revue de lancement à
-- laquelle ils sont maintenant affichés/rattachés.
--
-- IMPORTANT : le champ is_inv_achat_moule.revue_lancementid n'est PAS fiable à lui
-- seul pour détecter ces cas, car il n'est resynchronisé qu'au clic sur le bouton
-- "Diffuser" (méthode creation_inv_achat_moule, appelée par action_vers_diffuse).
-- Tant que ce bouton n'est pas recliqué après une copie fautive, revue_lancementid
-- continue de pointer vers l'ancienne revue de lancement (chez qui le moule est
-- cohérent), et une comparaison basée uniquement sur cette colonne ne voit donc pas
-- l'incohérence pourtant visible dans le formulaire de la NOUVELLE revue de
-- lancement (section "Liens").
--
-- Ce script combine donc DEUX détections pour ne rien manquer :
--   1) "lien affiché"      : à partir des 18 champs rl_be01_id..rl_be17_id de
--                            is_revue_lancement (le lien réellement affiché à
--                            l'utilisateur dans le formulaire de la RL).
--   2) "lien revue_lancementid" : à partir de is_inv_achat_moule.revue_lancementid,
--                            qui peut détecter des enregistrements devenus
--                            orphelins (non référencés par aucun rl_be0X_id actuel)
--                            mais dont le revue_lancementid pointe encore vers une
--                            RL avec laquelle le moule/dossier F ne correspond plus.
-- Dans les deux cas, le moule / dossier F de référence est celui de la revue de
-- contrat (is.revue.de.contrat) associée à la RL (rl_num_rcid -> rc_mouleid /
-- rc_dossierfid), avec repli sur le champ dossierf_id de la RL si la revue de
-- contrat n'a pas de dossier F renseigné.
--
-- Lecture seule : aucune modification n'est effectuée par ce script.

WITH rl_ref AS (
    SELECT
        rl.id                                       AS rl_id,
        rl.name                                     AS rl_name,
        rc.rc_mouleid                                AS ref_mouleid,
        COALESCE(rc.rc_dossierfid, rl.dossierf_id)   AS ref_dossierfid,
        rl.rl_be01_id  AS be01_id,  rl.rl_be01b_id AS be01b_id, rl.rl_be01c_id AS be01c_id,
        rl.rl_be02_id  AS be02_id,  rl.rl_be03_id  AS be03_id,  rl.rl_be04_id  AS be04_id,
        rl.rl_be05_id  AS be05_id,  rl.rl_be06_id  AS be06_id,  rl.rl_be07_id  AS be07_id,
        rl.rl_be09_id  AS be09_id,  rl.rl_be10_id  AS be10_id,  rl.rl_be11_id  AS be11_id,
        rl.rl_be12_id  AS be12_id,  rl.rl_be13_id  AS be13_id,  rl.rl_be14_id  AS be14_id,
        rl.rl_be15_id  AS be15_id,  rl.rl_be16_id  AS be16_id,  rl.rl_be17_id  AS be17_id
    FROM is_revue_lancement rl
    LEFT JOIN is_revue_de_contrat rc ON rc.id = rl.rl_num_rcid
),
rl_links AS (
    SELECT rl_id, rl_name, ref_mouleid, ref_dossierfid, 'be01'  AS code_imputation, be01_id  AS achat_moule_id FROM rl_ref WHERE be01_id  IS NOT NULL
    UNION ALL SELECT rl_id, rl_name, ref_mouleid, ref_dossierfid, 'be01b', be01b_id FROM rl_ref WHERE be01b_id IS NOT NULL
    UNION ALL SELECT rl_id, rl_name, ref_mouleid, ref_dossierfid, 'be01c', be01c_id FROM rl_ref WHERE be01c_id IS NOT NULL
    UNION ALL SELECT rl_id, rl_name, ref_mouleid, ref_dossierfid, 'be02',  be02_id  FROM rl_ref WHERE be02_id  IS NOT NULL
    UNION ALL SELECT rl_id, rl_name, ref_mouleid, ref_dossierfid, 'be03',  be03_id  FROM rl_ref WHERE be03_id  IS NOT NULL
    UNION ALL SELECT rl_id, rl_name, ref_mouleid, ref_dossierfid, 'be04',  be04_id  FROM rl_ref WHERE be04_id  IS NOT NULL
    UNION ALL SELECT rl_id, rl_name, ref_mouleid, ref_dossierfid, 'be05',  be05_id  FROM rl_ref WHERE be05_id  IS NOT NULL
    UNION ALL SELECT rl_id, rl_name, ref_mouleid, ref_dossierfid, 'be06',  be06_id  FROM rl_ref WHERE be06_id  IS NOT NULL
    UNION ALL SELECT rl_id, rl_name, ref_mouleid, ref_dossierfid, 'be07',  be07_id  FROM rl_ref WHERE be07_id  IS NOT NULL
    UNION ALL SELECT rl_id, rl_name, ref_mouleid, ref_dossierfid, 'be09',  be09_id  FROM rl_ref WHERE be09_id  IS NOT NULL
    UNION ALL SELECT rl_id, rl_name, ref_mouleid, ref_dossierfid, 'be10',  be10_id  FROM rl_ref WHERE be10_id  IS NOT NULL
    UNION ALL SELECT rl_id, rl_name, ref_mouleid, ref_dossierfid, 'be11',  be11_id  FROM rl_ref WHERE be11_id  IS NOT NULL
    UNION ALL SELECT rl_id, rl_name, ref_mouleid, ref_dossierfid, 'be12',  be12_id  FROM rl_ref WHERE be12_id  IS NOT NULL
    UNION ALL SELECT rl_id, rl_name, ref_mouleid, ref_dossierfid, 'be13',  be13_id  FROM rl_ref WHERE be13_id  IS NOT NULL
    UNION ALL SELECT rl_id, rl_name, ref_mouleid, ref_dossierfid, 'be14',  be14_id  FROM rl_ref WHERE be14_id  IS NOT NULL
    UNION ALL SELECT rl_id, rl_name, ref_mouleid, ref_dossierfid, 'be15',  be15_id  FROM rl_ref WHERE be15_id  IS NOT NULL
    UNION ALL SELECT rl_id, rl_name, ref_mouleid, ref_dossierfid, 'be16',  be16_id  FROM rl_ref WHERE be16_id  IS NOT NULL
    UNION ALL SELECT rl_id, rl_name, ref_mouleid, ref_dossierfid, 'be17',  be17_id  FROM rl_ref WHERE be17_id  IS NOT NULL
),

-- 1) Anomalies détectées via le lien réellement affiché (rl_be0X_id)
anomalies_lien_affiche AS (
    SELECT
        'RL'                           AS origine,
        l.rl_name                     AS revue_lancement,
        l.code_imputation,
        rl_moule.name                 AS moule_attendu,
        rl_dossierf.name              AS dossierf_attendu,
        achat_moule.name              AS moule_lien,
        achat_dossierf.name           AS dossierf_lien,
        rl_lien.name                  AS revue_lancement_du_lien
    FROM rl_links l
    INNER JOIN is_inv_achat_moule m      ON m.id = l.achat_moule_id
    LEFT JOIN is_mold achat_moule        ON achat_moule.id = m.num_mouleid
    LEFT JOIN is_dossierf achat_dossierf ON achat_dossierf.id = m.dossierf_id
    LEFT JOIN is_mold rl_moule           ON rl_moule.id = l.ref_mouleid
    LEFT JOIN is_dossierf rl_dossierf    ON rl_dossierf.id = l.ref_dossierfid
    LEFT JOIN is_revue_lancement rl_lien ON rl_lien.id = m.revue_lancementid
    WHERE
        (m.num_mouleid IS DISTINCT FROM l.ref_mouleid)
        OR (m.dossierf_id IS DISTINCT FROM l.ref_dossierfid)
),

-- 2) Anomalies détectées via revue_lancementid (dont les éventuels orphelins,
--    non référencés par aucun rl_be0X_id actuel)
anomalies_revue_lancementid AS (
    SELECT
        'INV'                          AS origine,
        rl.name                       AS revue_lancement,
        m.code_imputation             AS code_imputation,
        rl_moule.name                 AS moule_attendu,
        rl_dossierf.name              AS dossierf_attendu,
        achat_moule.name              AS moule_lien,
        achat_dossierf.name           AS dossierf_lien,
        rl.name                       AS revue_lancement_du_lien
    FROM is_inv_achat_moule m
    INNER JOIN is_revue_lancement rl     ON rl.id = m.revue_lancementid
    LEFT JOIN is_revue_de_contrat rc     ON rc.id = rl.rl_num_rcid
    LEFT JOIN is_mold achat_moule        ON achat_moule.id = m.num_mouleid
    LEFT JOIN is_dossierf achat_dossierf ON achat_dossierf.id = m.dossierf_id
    LEFT JOIN is_mold rl_moule           ON rl_moule.id = rc.rc_mouleid
    LEFT JOIN is_dossierf rl_dossierf    ON rl_dossierf.id = COALESCE(rc.rc_dossierfid, rl.dossierf_id)
    WHERE
        (m.num_mouleid IS DISTINCT FROM rc.rc_mouleid)
        OR (m.dossierf_id IS DISTINCT FROM COALESCE(rc.rc_dossierfid, rl.dossierf_id))
)

SELECT * FROM anomalies_lien_affiche
UNION
SELECT * FROM anomalies_revue_lancementid
ORDER BY origine, revue_lancement, code_imputation;
