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
# CONDITION — Only Apply to Company Name
# ============================================================

def company_name_condition(param: Parameter) -> bool:
    return param.name == "Company Name"


# ============================================================
# TC-1.2-COMPANYNAME-01
# Reject Empty String ("")
# ============================================================

def tc_1_2_companyname_01_validator(param: Parameter):
    if param.value == "":
        return (
            "Empty string detected — Violates Not Null rule and "
            "business requirement: Must match official registration"
        )
    return True


TC_1_2_COMPANYNAME_01 = MasterTestCase(
    test_id="TC-1.2-COMPANYNAME-01",
    applicability=Applicability.CONDITIONAL,
    condition=company_name_condition,
    validator=tc_1_2_companyname_01_validator
)


# ============================================================
# TC-1.2-COMPANYNAME-02
# Reject Whitespace Only ("   ")
# ============================================================

def tc_1_2_companyname_02_validator(param: Parameter):
    if isinstance(param.value, str) and param.value.strip() == "":
        return (
            "Whitespace-only value detected — Must contain valid legal "
            "name characters per regex"
        )
    return True


TC_1_2_COMPANYNAME_02 = MasterTestCase(
    test_id="TC-1.2-COMPANYNAME-02",
    applicability=Applicability.CONDITIONAL,
    condition=company_name_condition,
    validator=tc_1_2_companyname_02_validator
)


# ============================================================
# TC-1.2-COMPANYNAME-03
# Reject NULL
# ============================================================

def tc_1_2_companyname_03_validator(param: Parameter):
    if param.value is None:
        return (
            "NULL value detected — Required legal identity field"
        )
    return True


TC_1_2_COMPANYNAME_03 = MasterTestCase(
    test_id="TC-1.2-COMPANYNAME-03",
    applicability=Applicability.CONDITIONAL,
    condition=company_name_condition,
    validator=tc_1_2_companyname_03_validator
)


# ============================================================
# REGISTER TEST CASES
# ============================================================

ALL_1_2_COMPANYNAME_TESTS = [
    TC_1_2_COMPANYNAME_01,
    TC_1_2_COMPANYNAME_02,
    TC_1_2_COMPANYNAME_03
]


# ============================================================
# RULE ENGINE EXECUTION
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
# PYTEST FIXTURE (Replace with real loader in production)
# ============================================================

@pytest.fixture
def dataset():
    return Dataset(parameters=[
        Parameter("P001", "Company Name", "", {}),
        Parameter("P002", "Company Name", "   ", {}),
        Parameter("P003", "Company Name", None, {})
    ])


# ============================================================
# PYTEST EXECUTION
# ============================================================

# For negative tests we expect the validator to reject invalid data (report failures).
EXPECTED_NEGATIVE_FAILURES = {
    "TC-1.2-COMPANYNAME-01": {"P001"},   # empty string
    "TC-1.2-COMPANYNAME-02": {"P001", "P002"},  # whitespace-only
    "TC-1.2-COMPANYNAME-03": {"P003"},   # null
}


@pytest.mark.parametrize("test_case", ALL_1_2_COMPANYNAME_TESTS)
def test_company_name_negative_validation(dataset, test_case):
    failures = evaluate_conditional(test_case, dataset)
    failed_ids = {pid for pid, _ in failures}
    expected = EXPECTED_NEGATIVE_FAILURES.get(test_case.test_id, set())

    assert failed_ids == expected, (
        f"\nNegative validation: expected failures for {expected}, got {failed_ids}\n"
        f"Test Case: {test_case.test_id}\n"
        f"Failures:\n" +
        "\n".join(f"Parameter {pid}: {reason}" for pid, reason in failures)
    )