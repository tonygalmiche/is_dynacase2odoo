-- Objectif :
-- Suite à des copies de "Revue de lancement" (is.revue.lancement), les champs
-- rl_be01_id à rl_be17_id de is.inv.achat.moule (liés via revue_lancementid)
-- ont été copiés alors qu'ils ne l'auraient pas dû (correction copy=False depuis).
-- Ces investissements achat moule (is_inv_achat_moule) pointent donc encore
-- vers le moule / dossier F de la revue de lancement d'origine, et non plus
-- vers celui de la nouvelle revue de lancement à laquelle ils sont maintenant
-- rattachés (via revue_lancementid).
--
-- Ce script identifie tous les is.inv.achat.moule dont le moule ou le dossier F
-- ne correspond pas au moule / dossier F de la revue de contrat (is.revue.de.contrat)
-- liée à leur revue de lancement (rl_num_rcid -> rc_mouleid / rc_dossierfid),
-- avec repli sur le champ dossierf_id de la revue de lancement si la revue de
-- contrat n'a pas de dossier F renseigné.
--
-- Lecture seule : aucune modification n'est effectuée par ce script.

SELECT
    rl.name                    AS revue_lancement,
    achat_moule.name           AS moule,
    achat_dossierf.name        AS dossierf,
    rl_moule.name              AS moule_rl,
    rl_dossierf.name           AS dossierf_rl
FROM is_inv_achat_moule m
INNER JOIN is_revue_lancement rl        ON rl.id = m.revue_lancementid
LEFT JOIN is_revue_de_contrat rc        ON rc.id = rl.rl_num_rcid
LEFT JOIN is_mold achat_moule           ON achat_moule.id = m.num_mouleid
LEFT JOIN is_dossierf achat_dossierf    ON achat_dossierf.id = m.dossierf_id
LEFT JOIN is_mold rl_moule              ON rl_moule.id = rc.rc_mouleid
LEFT JOIN is_dossierf rl_dossierf       ON rl_dossierf.id = COALESCE(rc.rc_dossierfid, rl.dossierf_id)
WHERE
    (m.num_mouleid IS DISTINCT FROM rc.rc_mouleid)
    OR (m.dossierf_id IS DISTINCT FROM COALESCE(rc.rc_dossierfid, rl.dossierf_id))
ORDER BY rl.name;
