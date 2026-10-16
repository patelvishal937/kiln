"""Typed hand-offs between phases. Every agent phase must submit one of these."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Intent = Literal["informational", "commercial", "transactional", "navigational"]
PageType = Literal["blog post", "guide", "comparison page", "FAQ page", "landing page"]


# ---------------------------------------------------------------- 1. intake
SourceKind = Literal["idea", "website", "apk"]


class Brief(BaseModel):
    working_name: str = Field(description="Product name if given, else a short working name")
    one_liner: str
    problem: str
    target_customers: list[str] = Field(min_length=1)
    core_features: list[str] = Field(min_length=1, description="What a user can DO, verb-first")
    monetization: str = Field(description="free / freemium / subscription with price idea / one-time / unknown")
    tone: str
    language: str = "English"
    geography: str = "Global"
    known_competitors: list[str] = []
    constraints: list[str] = []
    wants_app: bool = True
    wants_site: bool = True
    wants_videos: bool = True
    wants_emails: bool = True
    assumptions: list[str] = Field(default=[], description="Things you assumed instead of asking")
    # reverse-engineer context (idea mode leaves these empty)
    source_kind: SourceKind = "idea"
    source_ref: str = Field(default="", description="URL (website) or file path (apk) of the product being rebuilt")
    rebuild_goal: str = Field(default="", description="What the rebuild should KEEP, CHANGE and IMPROVE vs the original")
    original_name_to_avoid: str = Field(default="", description="Original brand/trademark the rebuild must NOT reuse")


# ------------------------------------------------- reverse-engineer: Teardown
class IANode(BaseModel):
    name: str
    locator: str = Field(description="route/path for a site, or screen/activity name for an app")
    purpose: str


class ScreenSpec(BaseModel):
    name: str
    role: str = Field(description="what the user does here")
    elements: list[str] = Field(description="the notable UI building blocks, not pixel detail")
    notes: str = ""


class Flow(BaseModel):
    name: str
    steps: list[str] = Field(min_length=2)


class EntitySpec(BaseModel):
    name: str
    fields: list[str]
    inferred_from: str = Field(default="", description="what evidence suggested this entity")


class DesignLanguage(BaseModel):
    colors: list[str] = Field(default=[], description="hex values observed")
    fonts: list[str] = []
    style_notes: str = ""


class Teardown(BaseModel):
    """A structural map of an existing product, used to rebuild an ORIGINAL equivalent.

    This captures how a product is put together — its jobs, screens, flows, data and
    tech — never its proprietary branding, copy or assets, which the rebuild recreates
    from scratch under a new name.
    """

    source_kind: Literal["website", "apk"]
    source_ref: str
    product_summary: str
    primary_jobs: list[str] = Field(min_length=1, description="jobs-to-be-done the product serves")
    information_architecture: list[IANode] = Field(min_length=1)
    key_screens: list[ScreenSpec] = Field(min_length=1)
    core_flows: list[Flow] = Field(min_length=1)
    data_entities: list[EntitySpec] = Field(min_length=1)
    tech_signals: list[str] = Field(default=[], description="framework / stack hints observed")
    design_language: DesignLanguage = DesignLanguage()
    content_model: list[str] = Field(default=[], description="recurring content types")
    integrations_detected: list[str] = []
    strengths: list[str] = []
    gaps: list[str] = Field(default=[], description="weaknesses the rebuild can beat")
    rebuild_notes: str = Field(description="how to build an original equivalent on Greta")
    do_not_copy: list[str] = Field(
        default=[],
        description="trademarks, verbatim copy, logos or assets the rebuild must recreate originally, never reuse",
    )
    confidence_notes: str = ""


# ---------------------------------------------------------------- 2. research
class Competitor(BaseModel):
    name: str
    url: str = ""
    positioning: str
    pricing: str = "unknown"
    strengths: list[str] = []
    weaknesses: list[str] = []


class Pain(BaseModel):
    pain: str
    evidence: str = Field(description="Quote or paraphrase + where it came from")
    source_url: str = ""


class KeywordIdea(BaseModel):
    keyword: str
    intent: Intent
    difficulty_estimate: Optional[float] = Field(default=None, ge=0, le=100)
    volume_hint: str = ""
    why: str = ""


class Research(BaseModel):
    competitors: list[Competitor] = Field(min_length=1)
    customer_pains: list[Pain] = Field(min_length=1)
    keyword_ideas: list[KeywordIdea] = Field(min_length=5)
    must_have_features: list[str]
    differentiation_angles: list[str] = Field(min_length=1)
    pricing_benchmarks: list[str] = []
    sources: list[str] = Field(min_length=1)
    used_apify: bool = False
    confidence_notes: str = ""


# ---------------------------------------------------------------- 3. blueprint
class BrandColors(BaseModel):
    primary: str
    secondary: str
    accent: str
    background: str
    text: str


class Brand(BaseModel):
    name: str
    tagline: str
    voice: str
    colors: BrandColors
    heading_font: str
    body_font: str
    logo_concept: str


class DataModel(BaseModel):
    name: str
    fields: list[str]


class AppPage(BaseModel):
    route: str
    purpose: str


class AppSpec(BaseModel):
    summary: str
    user_roles: list[str]
    data_models: list[DataModel] = Field(min_length=1)
    pages: list[AppPage] = Field(min_length=2)
    mvp_features: list[str] = Field(min_length=1)
    auth: str
    payments: str = "none"
    build_milestones: list[str] = Field(
        min_length=2,
        max_length=6,
        description="Each item is a complete, self-contained instruction message to the Greta builder",
    )
    acceptance_checks: list[str] = Field(min_length=2, description="Things to click through to call the app done")


class SitePage(BaseModel):
    route: str
    purpose: str
    key_sections: list[str]


class SitePlan(BaseModel):
    pages: list[SitePage] = Field(min_length=3)
    primary_cta: str
    lead_capture: str = "Greta Forms waitlist/contact form"
    build_prompt: str = Field(description="The full first-turn prompt for the self-growing site")


class SeoTask(BaseModel):
    title: str = Field(max_length=120)
    brief: str = Field(min_length=20, max_length=1500)
    target_keyword: str = Field(max_length=120)
    search_intent: Intent
    page_type: PageType = "blog post"
    priority: Literal["High", "Medium", "Low"] = "Medium"
    difficulty: Optional[float] = Field(default=None, ge=0, le=100)
    week: int = Field(ge=1, le=12)


class DemoScene(BaseModel):
    title: str = Field(max_length=40)
    caption: str = Field(max_length=110)
    screen: Literal["app", "site"] = "app"
    route: str = "/"


class VideoPlan(BaseModel):
    demo_scenes: list[DemoScene] = Field(min_length=3, max_length=7)
    hook_line: str = Field(max_length=60)
    cta_line: str = Field(max_length=50)
    hero_loop_prompt: str
    avatar_script: str = Field(description="45-75 second spoken explainer script")


class EmailStep(BaseModel):
    name: str
    trigger: str
    delay_hours: int = 0
    subject: str
    goal: str
    key_points: list[str]


class Blueprint(BaseModel):
    brand: Brand
    positioning: str
    pricing: str
    app: AppSpec
    site: SitePlan
    seo_calendar: list[SeoTask] = Field(min_length=6, max_length=24)
    video: VideoPlan
    emails: list[EmailStep] = Field(min_length=3, max_length=6)
    launch_channels: list[str]


# ---------------------------------------------------------------- 4-5. builds
class AppResult(BaseModel):
    conversation_id: str
    workspace_url: str = ""
    preview_url: str = ""
    backend_url: str = ""
    deployment_id: str = ""
    milestones_completed: list[int] = []
    acceptance_status: dict[str, str] = {}
    open_issues: list[str] = []
    human_todos: list[str] = []


class SiteResult(BaseModel):
    conversation_id: str
    workspace_url: str = ""
    live_url: str = ""
    published: bool = False
    publish_blocker: str = ""
    growth_loop_enabled: bool = False
    growth_tasks_added: int = 0
    growth_authority: str = Field(default="", description="nightly-loop or automatic-growth (Fenn)")
    open_issues: list[str] = []
    human_todos: list[str] = []


# ---------------------------------------------------------------- 6-7. media
class MediaResult(BaseModel):
    screenshots: list[str] = []
    demo_video: str = ""
    demo_video_vertical: str = ""
    hero_video: str = ""
    avatar_video: str = ""
    poster_image: str = ""
    public_urls: dict[str, str] = {}
    skipped: list[str] = []


class HeroVideoResult(BaseModel):
    video_url: str
    poster_url: str = ""
    notes: str = ""


class EmbedResult(BaseModel):
    embedded: list[str] = []
    republished: bool = False
    open_issues: list[str] = []
    human_todos: list[str] = []


# ---------------------------------------------------------------- 8. email
class EmailResult(BaseModel):
    templates: list[str] = []
    workflows: list[str] = []
    test_send_verified: bool = False
    integration_snippet: str = Field(default="", description="How the app should fire the signup event")
    human_todos: list[str] = []


# ---------------------------------------------------------------- 9. qa
class QACheck(BaseModel):
    target: str
    check: str
    ok: bool
    detail: str = ""


class QAResult(BaseModel):
    checks: list[QACheck] = []
    fixes_requested: list[str] = []
    still_failing: list[str] = []


class QAFixResult(BaseModel):
    fixes_requested: list[str] = []
    verified_fixed: list[str] = []
    still_failing: list[str] = []


# ---------------------------------------------------------------- 10. launch kit
class LaunchKit(BaseModel):
    product_hunt_tagline: str = Field(max_length=60)
    product_hunt_description: str = Field(max_length=260)
    product_hunt_first_comment: str
    x_thread: list[str] = Field(min_length=4, max_length=10)
    linkedin_post: str
    reddit_angles: list[str] = Field(min_length=2)
    cold_email: str
    short_video_captions: list[str] = Field(min_length=3)
