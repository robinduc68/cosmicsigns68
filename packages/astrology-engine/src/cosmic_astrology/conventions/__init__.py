"""Convention profiles — every school-dependent choice, named and versioned."""

from cosmic_astrology.conventions.nam_phai import (
    COSMIC_SIGNS_NAM_PHAI_V1,
    NAM_PHAI_PROFILE_ID,
    NAM_PHAI_PROFILE_VERSION,
)
from cosmic_astrology.conventions.policies import (
    BirthTimeCorrectionPolicy,
    LateZiPolicy,
    RuleId,
    TimezonePolicy,
    VerificationStatus,
)
from cosmic_astrology.conventions.profile import (
    ConventionProfile,
    ProfileValidation,
    RecalculationCheck,
    RuleBinding,
    UnresolvedConventionError,
    is_production_ready,
    needs_recalculation,
    validate_convention_profile,
)
from cosmic_astrology.conventions.provenance import NO_SOURCE_YET, SourceReference
from cosmic_astrology.conventions.standard import (
    COSMIC_SIGNS_STANDARD_V1,
    STANDARD_PROFILE_ID,
    STANDARD_PROFILE_VERSION,
)

__all__ = [
    "COSMIC_SIGNS_NAM_PHAI_V1",
    "COSMIC_SIGNS_STANDARD_V1",
    "NAM_PHAI_PROFILE_ID",
    "NAM_PHAI_PROFILE_VERSION",
    "NO_SOURCE_YET",
    "STANDARD_PROFILE_ID",
    "STANDARD_PROFILE_VERSION",
    "BirthTimeCorrectionPolicy",
    "ConventionProfile",
    "LateZiPolicy",
    "ProfileValidation",
    "RecalculationCheck",
    "RuleBinding",
    "RuleId",
    "SourceReference",
    "TimezonePolicy",
    "UnresolvedConventionError",
    "VerificationStatus",
    "is_production_ready",
    "needs_recalculation",
    "validate_convention_profile",
]
