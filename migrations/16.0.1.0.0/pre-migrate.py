def migrate(cr, version):
    if not version:
        return

    # Workflow simplifié PLAN => DO => CHECK : l'état Act disparaît, les actions Act passent en Check
    cr.execute("UPDATE is_action SET state='check' WHERE state='act'")

    # Le champ « action préventive ou transversalisable » est supprimé : son contenu est ajouté
    # à la fin de l'objectif, séparé par une ligne vide
    cr.execute("""
        UPDATE is_plan_action
        SET obj = CASE
                WHEN coalesce(trim(obj), '') = '' THEN action_prev
                ELSE obj || E'\\n\\n' || action_prev
            END,
            action_prev = NULL
        WHERE coalesce(trim(action_prev), '') <> ''
    """)
