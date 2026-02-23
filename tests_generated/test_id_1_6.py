import pytest
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class Parameter:
    parameter_id: str
    name: str
    value: Any
    metadata: Dict[str, Any]


@dataclass
class Dataset:
    parameters: List[Parameter]


# ============================================================
# MASTER TEST STRUCTURE
# ============================================================

class Applicability:
    CONDITIONAL = "conditional"


class MasterTestCase:
    def __init__(self, test_id: str, applicability: str, condition, validator):
        self.test_id = test_id
        self.applicability = applicability
        self.condition = condition
        self.validator = validator


# ============================================================
# CONDITION — Applies Only To Company Name
# ============================================================

def company_name_condition(param: Parameter) -> bool:
    return param.name == "Company Name"


# ============================================================
# OFFICIAL COMPANY REGISTRY (Simulated)
# ============================================================

OFFICIAL_COMPANY_NAMES = {
    "Microsoft Corporation",
    "Microsoft Corp.",
    "Apple Inc.",
    "Google LLC",
    "Tesla, Inc.",
}


# ============================================================
# HELPER: Normalize case to Standard Case (lower then title)
# ============================================================

def normalize_case(value: str) -> str:
    return value.strip().lower().title()


# ============================================================
# TC-CASE-COMPANYNAME-01
# Lowercase input — should normalize
# ============================================================

def tc_case_companyname_01_validator(param: Parameter):
    value = param.value
    normalized = normalize_case(value)

    if normalized not in OFFICIAL_COMPANY_NAMES:
        return f"Normalized '{normalized}' does not match official company names"
    return True


# ============================================================
# TC-CASE-COMPANYNAME-02
# Uppercase input — should normalize
# ============================================================

def tc_case_companyname_02_validator(param: Parameter):
    value = param.value
    normalized = normalize_case(value)

    if normalized not in OFFICIAL_COMPANY_NAMES:
        return f"Normalized '{normalized}' does not match official company names"
    return True


# ============================================================
# TC-CASE-COMPANYNAME-03
# Mixed-case input — normalize & validate
# ============================================================

def tc_case_companyname_03_validator(param: Parameter):
    value = param.value
    normalized = normalize_case(value)

    if normalized not in OFFICIAL_COMPANY_NAMES:
        return f"Normalized '{normalized}' does not match official company names"
    return True


# ============================================================
# TC-CASE-COMPANYNAME-04
# Reject if case variation breaks legal match
# ============================================================

def tc_case_companyname_04_validator(param: Parameter):
    value = param.value
    normalized = normalize_case(value)

    # Simulate fuzzy match confidence threshold
    if normalized not in OFFICIAL_COMPANY_NAMES:
        return "Case variation breaks legal identity match — Fail"
    return True


# ============================================================
# TC-CASE-COMPANYNAME-05
# Auto-correct inconsistent case
# ============================================================

def tc_case_companyname_05_validator(param: Parameter):
    value = param.value
    corrected = normalize_case(value)

    if corrected not in OFFICIAL_COMPANY_NAMES:
        return f"Auto-corrected '{corrected}' does not match official company names"
    return True


# ============================================================
# REGISTER TEST CASES
# ============================================================

ALL_CASE_COMPANYNAME_TESTS = [
    MasterTestCase("TC-CASE-COMPANYNAME-01", Applicability.CONDITIONAL, company_name_condition, tc_case_companyname_01_validator),
    MasterTestCase("TC-CASE-COMPANYNAME-02", Applicability.CONDITIONAL, company_name_condition, tc_case_companyname_02_validator),
    MasterTestCase("TC-CASE-COMPANYNAME-03", Applicability.CONDITIONAL, company_name_condition, tc_case_companyname_03_validator),
    MasterTestCase("TC-CASE-COMPANYNAME-04", Applicability.CONDITIONAL, company_name_condition, tc_case_companyname_04_validator),
    MasterTestCase("TC-CASE-COMPANYNAME-05", Applicability.CONDITIONAL, company_name_condition, tc_case_companyname_05_validator),
]


# ============================================================
# RULE ENGINE
# ============================================================

def evaluate_conditional(test_case: MasterTestCase, dataset: Dataset) -> List[Tuple[str, str]]:
    failures = []
    for param in dataset.parameters:
        if test_case.condition(param):
            result = test_case.validator(param)
            if result is not True:
                failures.append((param.parameter_id, result))
    return failures


# ============================================================
# PYTEST FIXTURE (Replace with actual dataset loader)
# ============================================================

@pytest.fixture
def dataset():
    return Dataset(parameters=[
        Parameter("P001", "Company Name", "microsoft corporation", {}),
        Parameter("P002", "Company Name", "MICROSOFT CORPORATION", {}),
        Parameter("P003", "Company Name", "MiCrOsOfT Corporation", {}),
        Parameter("P004", "Company Name", "mIcRoSoFt corp.", {}),
        Parameter("P005", "Company Name", "aPPle iNC.", {})
    ])


# ============================================================
# PYTEST EXECUTION
# ============================================================

@pytest.mark.parametrize("test_case", ALL_CASE_COMPANYNAME_TESTS)
def test_company_name_case_handling(dataset, test_case):
    failures = evaluate_conditional(test_case, dataset)

    assert not failures, (
        f"\nValidation Failure\n"
        f"Test Case: {test_case.test_id}\n"
        f"Failures:\n" +
        "\n".join(f"Parameter {pid}: {reason}" for pid, reason in failures)
    )