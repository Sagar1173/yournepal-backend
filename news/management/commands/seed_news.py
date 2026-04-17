from django.core.management.base import BaseCommand
from django.db import transaction

from news.models import News, NewsCategory, NewsStatus


FLASH_NEWS_ITEMS = [
    {
        "title": "Cabinet clears emergency repairs after landslides block two major highways overnight.",
        "summary": "The government approved an urgent restoration package after overnight landslides cut traffic on two key highway sections linking Kathmandu with western districts. Road crews and security teams were deployed before dawn, while transport officials said temporary diversions would remain in place until debris removal and safety inspections are completed.",
        "image": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
        "source_url": "https://example.com/news/flash-highway-repairs",
    },
    {
        "title": "Central bank issues fresh warning as banks report sharp rise in short-term liquidity demand.",
        "summary": "Nepal Rastra Bank called senior lenders for an early review after several commercial banks reported unusually high short-term liquidity demand this week. Officials said payment systems remain stable, but added that closer monitoring will continue while treasury flows, interbank lending and credit demand are assessed through the weekend.",
        "image": "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?auto=format&fit=crop&w=1200&q=80",
        "source_url": "https://example.com/news/flash-central-bank-warning",
    },
    {
        "title": "Power authority restores most transmission lines after sudden storm disrupts evening supply.",
        "summary": "The national utility said most disrupted transmission lines were restored overnight after a sudden storm triggered faults in several districts. Engineers are still checking two smaller corridors and asked industrial customers to expect brief fluctuations, but household supply has largely normalized following emergency switching and repair work.",
        "image": "https://images.unsplash.com/photo-1473773508845-188df298d2d1?auto=format&fit=crop&w=1200&q=80",
        "source_url": "https://example.com/news/flash-power-restoration",
    },
    {
        "title": "Election office launches rapid voter roll verification drive in dense urban wards.",
        "summary": "Election officials began a rapid digital verification drive in several urban wards after local offices reported duplicate entries and incomplete address updates ahead of municipal planning deadlines. Teams will use mobile help desks over the next week, and the commission said corrected records should appear in the central system soon.",
        "image": "https://images.unsplash.com/photo-1495020689067-958852a7765e?auto=format&fit=crop&w=1200&q=80",
        "source_url": "https://example.com/news/flash-voter-roll-drive",
    },
    {
        "title": "Hospitals activate seasonal response plan as dengue surveillance alerts increase in valley districts.",
        "summary": "Major hospitals activated their seasonal preparedness plans after public health teams reported a noticeable increase in mosquito surveillance alerts across valley districts. Health officials said the situation is still manageable, though emergency rooms, laboratories and municipal outreach units have been placed on higher readiness for the coming weeks.",
        "image": "https://images.unsplash.com/photo-1516574187841-cb9cc2ca948b?auto=format&fit=crop&w=1200&q=80",
        "source_url": "https://example.com/news/flash-dengue-response",
    },
]


NEPAL_NEWS_ITEMS = [
    {
        "title": "Tourism board says spring trekking permits are trending above last year's level.",
        "summary": "Tourism officials said spring trekking permits are tracking above last year's pace, supported by stronger bookings from regional travelers and repeat visitors from Europe. Agencies expect the momentum to continue if weather conditions stay favorable, while local businesses on major routes are preparing for a longer and more evenly distributed season.",
        "image": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80",
        "source_url": "https://example.com/news/nepal-trekking-permits",
    },
    {
        "title": "Hydropower producers seek faster approval of seasonal export schedules before monsoon peak.",
        "summary": "Private and public hydropower producers have asked regulators to finalize regional export schedules before the monsoon peak raises generation capacity. Industry representatives said earlier coordination would reduce curtailment risk, improve planning for cross-border sales and help the grid manage surplus energy more efficiently during high inflow months.",
        "image": "https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&w=1200&q=80",
        "source_url": "https://example.com/news/nepal-hydropower-export-schedules",
    },
    {
        "title": "Bagmati municipalities begin joint review of waste collection contracts after resident complaints.",
        "summary": "A group of Bagmati municipalities has launched a joint review of waste collection contracts after repeated complaints about missed pickups and unmanaged roadside dumping. Local officials said the review will compare service quality, payment structures and emergency response rules before recommendations are sent to elected councils for action.",
        "image": "",
        "source_url": "https://example.com/news/nepal-waste-contract-review",
    },
    {
        "title": "Parliament committee calls education officials to explain scholarship delays in remote districts.",
        "summary": "A parliamentary committee has summoned senior education officials to explain delays in scholarship distribution for students in remote districts. Lawmakers said schools have reported missed timelines and uneven communication, while the ministry insists updated guidelines and verification steps will help funds reach eligible students more consistently this term.",
        "image": "",
        "source_url": "https://example.com/news/nepal-scholarship-delays",
    },
    {
        "title": "Farm cooperatives push for timely fertilizer delivery as paddy preparation begins in plains.",
        "summary": "Farm cooperatives across the plains are urging faster fertilizer delivery as households begin preparing land for paddy cultivation. Agricultural groups warned that late supply could raise production costs and reduce yields, while ministry officials said procurement and transport arrangements are being accelerated to avoid bottlenecks seen in previous seasons.",
        "image": "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?auto=format&fit=crop&w=1200&q=80",
        "source_url": "https://example.com/news/nepal-fertilizer-delivery",
    },
    {
        "title": "Kathmandu planners outline phased intersection upgrades to improve traffic flow before festivals.",
        "summary": "Kathmandu planners have unveiled phased upgrades for several congested intersections, saying targeted signal changes, lane markings and pedestrian controls could improve traffic flow before the festival season. City engineers said the first package focuses on high-delay corridors where modest redesigns may deliver faster relief than large construction works.",
        "image": "",
        "source_url": "https://example.com/news/nepal-traffic-upgrades",
    },
    {
        "title": "Province leaders renew call for budget room to prioritize local bridges and rural roads.",
        "summary": "Provincial leaders renewed pressure on the federal government to provide more budget flexibility for bridges and rural roads that connect agricultural markets, health posts and schools. Officials argued that smaller infrastructure projects are often delayed despite having immediate local impact and broad support from municipal representatives.",
        "image": "https://images.unsplash.com/photo-1489515217757-5fd1be406fef?auto=format&fit=crop&w=1200&q=80",
        "source_url": "https://example.com/news/nepal-local-infrastructure-budget",
    },
    {
        "title": "Civil aviation office studies extended airport operating hours during tourism surge.",
        "summary": "Civil aviation officials are studying whether selected domestic airports can extend operating hours during tourism peaks to ease pressure on morning schedules. Airlines and tour operators said longer windows could reduce delays and improve aircraft utilization, though staffing, weather constraints and airspace coordination remain key considerations.",
        "image": "",
        "source_url": "https://example.com/news/nepal-airport-hours",
    },
    {
        "title": "Community schools pilot digital attendance tools to reduce dropout tracking gaps.",
        "summary": "Several community schools have started piloting digital attendance tools aimed at identifying dropout risks earlier and improving coordination with parents. Education officials said the project is still small, but early feedback suggests teachers can respond faster when absences increase, especially in areas where seasonal migration disrupts learning continuity.",
        "image": "https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&w=1200&q=80",
        "source_url": "https://example.com/news/nepal-digital-attendance-tools",
    },
    {
        "title": "Tea producers in eastern hills report stronger export inquiries ahead of first flush shipments.",
        "summary": "Tea producers in eastern hill districts said export inquiries have improved ahead of the first flush shipments, supported by demand from specialty buyers in India and Europe. Growers remain cautious about transport costs and weather variability, but processors said price signals are better than they were at the start of last year.",
        "image": "",
        "source_url": "https://example.com/news/nepal-tea-export-inquiries",
    },
    {
        "title": "Local governments test riverbank warning systems before expected rise in pre-monsoon flows.",
        "summary": "Municipal teams in flood-prone areas are testing updated riverbank warning systems before pre-monsoon flows increase. Officials said the work includes siren checks, community messaging drills and revised evacuation maps, with emphasis on settlements where informal housing and damaged embankments make households especially vulnerable during sudden surges.",
        "image": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80",
        "source_url": "https://example.com/news/nepal-riverbank-warning-systems",
    },
    {
        "title": "Health ministry expands telemedicine support for mountain clinics facing specialist shortages.",
        "summary": "The health ministry is expanding telemedicine support for mountain clinics that struggle to retain specialist doctors year-round. Officials said the next phase will improve referral coordination and remote consultations for maternal health, chronic disease management and emergency triage, especially in districts where travel disruptions often delay treatment.",
        "image": "",
        "source_url": "https://example.com/news/nepal-telemedicine-expansion",
    },
    {
        "title": "Irrigation users ask for maintenance funding as canal repairs lag in key farming belts.",
        "summary": "Irrigation user groups have asked for dedicated maintenance funding after reporting slow progress on canal repairs in major farming belts. They said even minor structural damage can cut water availability during planting windows, while provincial authorities promised a faster technical review of the most critical sections.",
        "image": "",
        "source_url": "https://example.com/news/nepal-canal-maintenance",
    },
    {
        "title": "University researchers begin air quality mapping project across secondary cities.",
        "summary": "University researchers have begun a new air quality mapping project in several secondary cities to improve local pollution planning beyond Kathmandu Valley. The study will combine low-cost sensors with traffic and weather data, giving municipalities a better picture of seasonal exposure patterns and possible interventions.",
        "image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1200&q=80",
        "source_url": "https://example.com/news/nepal-air-quality-mapping",
    },
    {
        "title": "Small business groups welcome lower digital payment fees for neighborhood merchants.",
        "summary": "Small business groups have welcomed lower digital payment fees for neighborhood merchants, saying the change could help more shops keep electronic transactions active beyond major urban centers. Industry associations said lower costs matter most for low-value purchases, where previous charges discouraged both sellers and customers.",
        "image": "",
        "source_url": "https://example.com/news/nepal-digital-payment-fees",
    },
]


INTERNATIONAL_NEWS_ITEMS = [
    {
        "title": "Global markets steady as investors weigh mixed signals from major central banks.",
        "summary": "Global markets traded in a narrow range as investors compared mixed signals from major central banks on inflation, growth and future rate moves. Analysts said expectations remain sensitive to labor data and energy prices, while bond traders are watching whether policymakers maintain a cautious tone through the next round of meetings.",
        "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1200&q=80",
        "source_url": "https://example.com/news/international-global-markets",
    },
    {
        "title": "Diplomats extend ceasefire discussions after late-night regional security meetings.",
        "summary": "Diplomats extended ceasefire discussions after a new round of late-night regional security meetings ended without a final breakthrough. Mediators described the talks as cautious but constructive, saying both sides remain engaged on humanitarian access, prisoner exchanges and monitoring arrangements that could support a broader de-escalation framework.",
        "image": "",
        "source_url": "https://example.com/news/international-ceasefire-talks",
    },
    {
        "title": "Climate negotiators revisit loss and damage financing ahead of next summit cycle.",
        "summary": "Climate negotiators reopened talks on loss and damage financing as governments prepare for the next summit cycle. Delegates said the main challenge is balancing near-term support for vulnerable countries with long-term funding commitments, while technical teams continue working on delivery channels, oversight standards and contribution formulas.",
        "image": "https://images.unsplash.com/photo-1473448912268-2022ce9509d8?auto=format&fit=crop&w=1200&q=80",
        "source_url": "https://example.com/news/international-climate-finance",
    },
    {
        "title": "Technology regulators review new cross-border cloud contracts signed by major firms.",
        "summary": "Technology regulators in several jurisdictions are reviewing new cross-border cloud contracts signed by major firms, focusing on competition, data access and procurement fairness. Industry observers said the outcome could shape how multinational clients split workloads across providers, especially in sectors facing stricter security and sovereignty requirements.",
        "image": "",
        "source_url": "https://example.com/news/international-cloud-contract-review",
    },
    {
        "title": "Shipping groups say updated port screening rules may speed customs processing in Asia.",
        "summary": "Shipping groups said updated cargo screening rules at major Asian ports may ultimately speed customs processing by reducing inconsistent inspections and document errors. Logistics firms expect some initial adjustment costs, but believe clearer procedures could shorten turnaround times for high-volume routes if digital systems perform as planned.",
        "image": "https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=1200&q=80",
        "source_url": "https://example.com/news/international-port-screening-rules",
    },
    {
        "title": "European transit unions announce coordinated strikes over staffing and wage negotiations.",
        "summary": "Transit unions in several European capitals announced coordinated strike action after wage and staffing talks stalled with operators. Commuters are expected to face significant disruptions if negotiations fail to improve, while city officials urged both sides to keep emergency services and basic commuter corridors running during any walkouts.",
        "image": "",
        "source_url": "https://example.com/news/international-transit-strikes",
    },
    {
        "title": "Asian manufacturers raise concern over slower factory orders from key export markets.",
        "summary": "Manufacturers across parts of Asia are reporting softer factory orders from key export markets, adding pressure to hiring and inventory plans for the next quarter. Economists said companies are adjusting cautiously rather than cutting sharply, as uncertainty around consumer demand and shipping costs continues to cloud the outlook.",
        "image": "",
        "source_url": "https://example.com/news/international-factory-orders",
    },
    {
        "title": "UN agencies expand heat response planning as cities prepare for harsher summer extremes.",
        "summary": "UN agencies and city officials are expanding heat response planning as seasonal forecasts point to harsher summer extremes in several regions. Preparedness measures include public cooling centers, worker safety alerts and stronger coordination with health systems, particularly in dense urban areas where heat exposure can rise quickly.",
        "image": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1200&q=80",
        "source_url": "https://example.com/news/international-heat-response-planning",
    },
    {
        "title": "Trade officials discuss updated semiconductor supply safeguards with allied economies.",
        "summary": "Trade officials from several allied economies are discussing updated safeguards for semiconductor supply chains after recent disruptions highlighted the cost of concentration risk. The talks focus on stockpiles, investment incentives and common reporting rules that could help governments respond faster when critical components become scarce.",
        "image": "",
        "source_url": "https://example.com/news/international-semiconductor-safeguards",
    },
    {
        "title": "Large food importers increase grain tenders as weather risks unsettle commodity outlook.",
        "summary": "Several large food importers have increased grain tenders as weather risks and shipping uncertainty unsettle the commodity outlook. Analysts said governments are trying to secure coverage before volatility intensifies, though the timing of purchases could also influence prices if multiple buyers stay active in the market together.",
        "image": "",
        "source_url": "https://example.com/news/international-grain-tenders",
    },
    {
        "title": "Researchers unveil lower-cost battery design aimed at stabilizing grid storage expansion.",
        "summary": "Researchers and industry partners unveiled a lower-cost battery design they say could support wider grid storage deployment if pilot results hold. Energy analysts noted that durability, supply chain availability and recycling economics will matter as much as performance, especially for utilities planning multiyear investment programs.",
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
        "source_url": "https://example.com/news/international-battery-design",
    },
    {
        "title": "Major insurers reassess coastal risk models after another season of costly storms.",
        "summary": "Major insurers are reassessing coastal risk models after another season of costly storms pushed claims higher in several markets. Analysts said revisions could influence premiums, reinsurance terms and municipal borrowing costs, as governments and private firms face renewed questions about resilience spending and long-term exposure.",
        "image": "",
        "source_url": "https://example.com/news/international-coastal-risk-models",
    },
    {
        "title": "Regional lenders in Africa expand mobile banking partnerships to reach rural users.",
        "summary": "Regional lenders in Africa are expanding mobile banking partnerships to reach more rural users with savings, payments and small business services. Executives said adoption has been strongest where agent networks are reliable, while regulators are monitoring consumer protection, pricing and system resilience as volumes grow.",
        "image": "https://images.unsplash.com/photo-1556740749-887f6717d7e4?auto=format&fit=crop&w=1200&q=80",
        "source_url": "https://example.com/news/international-mobile-banking-partnerships",
    },
    {
        "title": "Arctic shipping study warns new routes may bring faster trade and higher environmental risk.",
        "summary": "A new Arctic shipping study says emerging routes may shorten some trade journeys but could also raise environmental and emergency response risks. Researchers called for tighter vessel standards, better weather intelligence and stronger cooperation among coastal states before commercial traffic grows more rapidly in fragile waters.",
        "image": "",
        "source_url": "https://example.com/news/international-arctic-shipping-study",
    },
    {
        "title": "Media groups test AI translation tools to speed multilingual coverage of global events.",
        "summary": "Media organizations are testing AI translation tools to speed multilingual coverage of major global events, particularly for live reporting and social distribution. Editors said the technology can improve reach and response times, but human review remains essential for nuance, legal risk and public trust in sensitive stories.",
        "image": "",
        "source_url": "https://example.com/news/international-ai-translation-tools",
    },
]


class Command(BaseCommand):
    help = "Seed the news app with short dummy records for flash, Nepal, and international categories."

    category_names = {
        "flash": "Flash",
        "nepal": "Nepal",
        "international": "International",
    }

    def handle(self, *args, **options):
        with transaction.atomic():
            categories = self.ensure_categories()
            created_count = self.seed_news(categories)

        total_count = News.objects.filter(status=NewsStatus.PUBLISHED).count()
        self.stdout.write(self.style.SUCCESS(f"Seed complete. Created {created_count} news items."))
        self.stdout.write(f"Published news total: {total_count}")

    def ensure_categories(self):
        categories = {}

        for slug, name in self.category_names.items():
            category, _ = NewsCategory.objects.get_or_create(
                slug=slug,
                defaults={"name": name},
            )
            categories[slug] = category

        return categories

    def seed_news(self, categories):
        records_to_create = []

        for slug, items in (
            ("flash", FLASH_NEWS_ITEMS),
            ("nepal", NEPAL_NEWS_ITEMS),
            ("international", INTERNATIONAL_NEWS_ITEMS),
        ):
            category = categories[slug]
            existing_titles = set(
                News.objects.filter(category=category, status=NewsStatus.PUBLISHED).values_list("title", flat=True)
            )

            for item in items:
                if item["title"] in existing_titles:
                    continue

                records_to_create.append(
                    News(
                        category=category,
                        title=item["title"],
                        summary=item["summary"],
                        image=item["image"],
                        source_url=item["source_url"],
                        status=NewsStatus.PUBLISHED,
                    )
                )

        if records_to_create:
            News.objects.bulk_create(records_to_create, batch_size=100)

        return len(records_to_create)
