from pydantic import BaseModel


class FirewallRuleStat(BaseModel):
    chain: str
    action: str
    comment: str | None = None
    bytes: int = 0
    packets: int = 0
    hit_counter: int = 0


class NatRuleStat(BaseModel):
    chain: str
    action: str
    comment: str | None = None
    bytes: int = 0
    packets: int = 0
    hit_counter: int = 0


class FirewallStatsResponse(BaseModel):
    router_id: int
    rules: list[FirewallRuleStat]


class NatStatsResponse(BaseModel):
    router_id: int
    rules: list[NatRuleStat]
