"""RT08-C : test direct de l'aide à la décision Odoo."""

def check_case(name, rules, ml, confidence, guarded,
               expected_source, expected_treatment):
    values = {
        "recovery_recommendation": rules,
        "ml_recommendation": ml,
        "ml_confidence": confidence,
        "textile_quality": "poor" if guarded else "good",
        "textile_condition": "clean",
        "hazard_level": "low",
    }

    scrap = env["stock.scrap"].new(values)

    # Fixer la recommandation métier du scénario.
    scrap.recovery_recommendation = rules

    # Exécuter la vraie méthode Odoo.
    scrap._compute_ml_decision_advice()

    source = scrap.ml_decision_source
    treatment = scrap.ml_suggested_treatment

    assert source == expected_source, (
        f"{name}: source={source}, attendu={expected_source}"
    )
    assert treatment == expected_treatment, (
        f"{name}: traitement={treatment}, attendu={expected_treatment}"
    )

    print(f"OK - {name}")
    print(f"  Source : {source}")
    print(f"  Traitement : {treatment}")


check_case(
    "ML au-dessus du seuil",
    "recycle", "reuse", 92.0, False,
    "ml", "reuse"
)

check_case(
    "ML en dessous du seuil",
    "recycle", "reuse", 65.0, False,
    "rules", "recycle"
)

check_case(
    "Confiance exactement 80%",
    "recycle", "reuse", 80.0, False,
    "ml", "reuse"
)

check_case(
    "Garde-fou prioritaire",
    "disposal", "reuse", 99.0, True,
    "rules", "disposal"
)

check_case(
    "Accord entre règles et ML",
    "reuse", "reuse", 95.0, False,
    "agreement", "reuse"
)

check_case(
    "Examen humain demandé",
    "review", "reuse", 95.0, False,
    "human", False
)

print("\nRT08-C : 6 tests réussis.")
