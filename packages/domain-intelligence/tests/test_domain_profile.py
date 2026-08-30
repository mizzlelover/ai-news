from domain_intelligence.models import DomainProfile, IntelligenceMode


def test_domain_profile_can_start_with_a_domain_seed() -> None:
    profile = DomainProfile(
        domain="数字文旅产业",
        domain_aliases=("数字旅游", "文旅数字化"),
    )

    assert profile.mode is IntelligenceMode.DOMAIN_FOUNDATION
    assert profile.decision_context is None
    assert profile.domain_aliases == ("数字旅游", "文旅数字化")
