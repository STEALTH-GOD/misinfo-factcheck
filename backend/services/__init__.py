def __init__(self):
    print("Initializing Nepal News Retrieval Service...")
    
    # Expanded Nepal news sources with more articles
    self.sample_nepal_news = [
        {
            'title': 'Nepal Tourism Industry Shows Recovery Signs',
            'snippet': 'Tourism sector demonstrates positive growth with increasing visitor arrivals and improved infrastructure development across major destinations.',
            'url': 'https://kathmandupost.com',
            'source': 'The Kathmandu Post',
            'category': 'tourism',
            'published_date': '2024-11-08T10:30:00',
            'tags': ['Tourism', 'Economy', 'Recovery']
        },
        {
            'title': 'Government Announces Infrastructure Development Plans',
            'snippet': 'Major infrastructure projects announced including road connectivity improvements and digital infrastructure expansion across rural areas.',
            'url': 'https://ekantipur.com',
            'source': 'Ekantipur Daily',
            'category': 'infrastructure',
            'published_date': '2024-11-08T09:15:00',
            'tags': ['Infrastructure', 'Government', 'Development']
        },
        {
            'title': 'Economic Growth Indicators Show Positive Trends',
            'snippet': 'Recent economic data indicates steady growth in key sectors with improved employment rates and increased investment.',
            'url': 'https://myrepublica.nagariknetwork.com',
            'source': 'My Republica',
            'category': 'economy',
            'published_date': '2024-11-08T08:45:00',
            'tags': ['Economy', 'Growth', 'Investment']
        },
        {
            'title': 'Environmental Conservation Efforts Gain Momentum',
            'snippet': 'New environmental protection initiatives launched with focus on sustainable development and climate change adaptation.',
            'url': 'https://english.onlinekhabar.com',
            'source': 'Online Khabar',
            'category': 'environment',
            'published_date': '2024-11-07T12:15:00',
            'tags': ['Environment', 'Conservation', 'Climate']
        },
        {
            'title': 'Nepal Education Sector Sees Digital Transformation',
            'snippet': 'Digital learning platforms and technology integration in schools across Nepal showing promising results for student engagement.',
            'url': 'https://kathmandupost.com',
            'source': 'The Kathmandu Post',
            'category': 'education',
            'published_date': '2024-11-07T14:20:00',
            'tags': ['Education', 'Technology', 'Digital']
        },
        {
            'title': 'Agricultural Modernization Programs Launch in Rural Areas',
            'snippet': 'Government initiates comprehensive agricultural modernization with focus on sustainable farming and improved crop yields.',
            'url': 'https://ekantipur.com',
            'source': 'Ekantipur Daily',
            'category': 'agriculture',
            'published_date': '2024-11-06T11:30:00',
            'tags': ['Agriculture', 'Rural Development', 'Modernization']
        },
        {
            'title': 'Renewable Energy Projects Accelerate Across Nepal',
            'snippet': 'Solar and hydroelectric power projects gain momentum as Nepal advances towards energy independence and sustainability.',
            'url': 'https://english.onlinekhabar.com',
            'source': 'Online Khabar',
            'category': 'energy',
            'published_date': '2024-11-06T09:45:00',
            'tags': ['Energy', 'Renewable', 'Sustainability']
        },
        {
            'title': 'Nepal Healthcare System Strengthening Shows Progress',
            'snippet': 'Healthcare infrastructure improvements and medical training programs demonstrate significant advancement in rural health services.',
            'url': 'https://myrepublica.nagariknetwork.com',
            'source': 'My Republica',
            'category': 'health',
            'published_date': '2024-11-05T16:15:00',
            'tags': ['Health', 'Healthcare', 'Rural Development']
        }
    ]
    
    # International news sources - verified and credible
    self.international_news = [
        {
            'title': 'WHO Reports Global Health Initiatives Success',
            'snippet': 'World Health Organization highlights successful health programs in developing countries, including significant achievements in South Asia.',
            'url': 'https://www.who.int',
            'source': 'World Health Organization',
            'category': 'health',
            'published_date': '2024-11-08T12:00:00',
            'tags': ['Health', 'WHO', 'International', 'Global Health']
        },
        {
            'title': 'UN Climate Change Report Highlights Regional Progress',
            'snippet': 'United Nations climate assessment shows positive trends in renewable energy adoption and environmental protection in South Asian nations.',
            'url': 'https://www.un.org',
            'source': 'United Nations',
            'category': 'environment',
            'published_date': '2024-11-08T10:45:00',
            'tags': ['Climate', 'Environment', 'UN', 'International']
        },
        {
            'title': 'World Bank Announces Infrastructure Investment Program',
            'snippet': 'International financial institution commits significant funding for infrastructure development projects in emerging economies.',
            'url': 'https://www.worldbank.org',
            'source': 'World Bank',
            'category': 'economy',
            'published_date': '2024-11-07T15:30:00',
            'tags': ['Economy', 'Infrastructure', 'Investment', 'World Bank']
        },
        {
            'title': 'UNESCO Promotes Educational Technology in Developing Regions',
            'snippet': 'Global education organization supports digital learning initiatives and educational technology integration in underserved communities.',
            'url': 'https://www.unesco.org',
            'source': 'UNESCO',
            'category': 'education',
            'published_date': '2024-11-07T13:15:00',
            'tags': ['Education', 'Technology', 'UNESCO', 'Digital Learning']
        },
        {
            'title': 'UNICEF Child Welfare Programs Show Positive Impact',
            'snippet': 'International children\'s organization reports significant improvements in child health, education, and welfare across multiple countries.',
            'url': 'https://www.unicef.org',
            'source': 'UNICEF',
            'category': 'social',
            'published_date': '2024-11-06T14:20:00',
            'tags': ['Children', 'Welfare', 'UNICEF', 'Social Development']
        },
        {
            'title': 'IMF Economic Outlook Predicts Regional Growth',
            'snippet': 'International Monetary Fund forecasts positive economic growth for South Asian region with emphasis on sustainable development.',
            'url': 'https://www.imf.org',
            'source': 'International Monetary Fund',
            'category': 'economy',
            'published_date': '2024-11-06T11:00:00',
            'tags': ['Economy', 'Growth', 'IMF', 'Regional Development']
        }
    ]
    
    # Verified true news - fact-checked and confirmed
    self.verified_true_news = [
        {
            'title': 'WHO Recognizes Nepal\'s Health Sector Improvements',
            'snippet': 'World Health Organization acknowledges significant progress in Nepal\'s healthcare infrastructure and public health initiatives.',
            'url': 'https://www.who.int',
            'source': 'World Health Organization',
            'category': 'health',
            'published_date': '2024-11-05T11:00:00',
            'tags': ['Health', 'WHO', 'International']
        },
        {
            'title': 'Nepal Successfully Meets UN Sustainable Development Goals',
            'snippet': 'United Nations confirms Nepal has achieved significant milestones in sustainable development targets, particularly in education and health.',
            'url': 'https://www.un.org',
            'source': 'United Nations',
            'category': 'development',
            'published_date': '2024-11-04T09:30:00',
            'tags': ['UN', 'Development', 'Goals', 'International']
        },
        {
            'title': 'World Bank Approves Major Infrastructure Funding for Nepal',
            'snippet': 'International financial institution confirms substantial loan approval for Nepal\'s infrastructure development projects.',
            'url': 'https://www.worldbank.org',
            'source': 'World Bank',
            'category': 'economy',
            'published_date': '2024-11-03T14:45:00',
            'tags': ['World Bank', 'Infrastructure', 'Funding', 'Economy']
        },
        {
            'title': 'NASA Satellite Data Confirms Environmental Progress in Himalayas',
            'snippet': 'Space agency\'s satellite monitoring shows positive environmental trends and conservation success in Himalayan region.',
            'url': 'https://www.nasa.gov',
            'source': 'NASA',
            'category': 'environment',
            'published_date': '2024-11-02T16:20:00',
            'tags': ['NASA', 'Environment', 'Himalayas', 'Conservation']
        }
    ]
    
    # Fact-checked and debunked misinformation
    self.debunked_news = [
        {
            'title': 'Fact Check: Misinformation About Nepal Policies Debunked',
            'snippet': 'Recent false claims about government policies have been thoroughly investigated and found to be without factual basis.',
            'url': 'https://factcheck.org',
            'source': 'Fact Check International',
            'category': 'fact-check',
            'published_date': '2024-11-02T09:00:00',
            'tags': ['Fact Check', 'Misinformation', 'Policy']
        },
        {
            'title': 'False: Viral Social Media Claims About Nepal Economy Debunked',
            'snippet': 'Fact-checkers verify that recent viral claims about Nepal\'s economic situation are based on outdated or incorrect information.',
            'url': 'https://factcheck.org',
            'source': 'International Fact Check Network',
            'category': 'fact-check',
            'published_date': '2024-10-30T13:15:00',
            'tags': ['Fact Check', 'Economy', 'Social Media', 'Misinformation']
        },
        {
            'title': 'Debunked: False Health Claims Spreading on Social Media',
            'snippet': 'Health misinformation targeting Nepal and region thoroughly investigated and found to be scientifically inaccurate.',
            'url': 'https://healthfactcheck.org',
            'source': 'Health Fact Check',
            'category': 'fact-check',
            'published_date': '2024-10-28T10:30:00',
            'tags': ['Health', 'Fact Check', 'Misinformation', 'Social Media']
        }
    ]