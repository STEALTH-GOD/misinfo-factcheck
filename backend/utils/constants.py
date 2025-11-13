# Trusted news sources for credibility scoring
TRUSTED_SOURCES = [
    'reuters.com', 'apnews.com', 'bbc.com', 'cnn.com', 'nytimes.com',
    'washingtonpost.com', 'guardian.com', 'npr.org', 'politifact.com',
    'snopes.com', 'factcheck.org', 'economist.com', 'wsj.com', 'abc.go.com',
    'cbsnews.com', 'nbcnews.com', 'usatoday.com', 'time.com', 'newsweek.com'
]

# Nepali trusted sources
NEPALI_TRUSTED_SOURCES = [
    'ekantipur.com', 'onlinekhabar.com', 'setopati.com', 'ratopati.com',
    'nepalnews.com', 'khabarhub.com', 'pahilopost.com', 'republica.com',
    'myrepublica.nagariknetwork.com', 'kathmandupost.com', 'ujyaaloonline.com',
    'annapurnapost.com', 'nagariknews.nagariknetwork.com'
]

UNRELIABLE_SOURCES = [
    'infowars.com', 'breitbart.com', 'naturalnews.com', 'beforeitsnews.com',
    'worldnetdaily.com', 'truthfeed.com', 'dailystormer.com', 'zerohedge.com'
]

# Language-specific keywords for stance detection
NEPALI_REFUTING_WORDS = [
    'गलत', 'झूटो', 'असत्य', 'भ्रामक', 'मिथ्या', 'निराधार', 'फर्जी',
    'होइन', 'छैन', 'भएको छैन', 'सत्य होइन', 'तथ्य होइन'
]

NEPALI_SUPPORTING_WORDS = [
    'सत्य', 'सहि', 'ठिक', 'पुष्टि', 'प्रमाणित', 'वैज्ञानिक', 'तथ्य',
    'अनुसन्धान', 'अध्ययन', 'विशेषज्ञ'
]

HINDI_REFUTING_WORDS = [
    'गलत', 'झूठ', 'असत्य', 'भ्रामक', 'मिथ्या', 'आधारहीन', 'नकली',
    'नहीं', 'गलत है', 'सच नहीं'
]

HINDI_SUPPORTING_WORDS = [
    'सत्य', 'सही', 'ठीक', 'पुष्टि', 'प्रमाणित', 'वैज्ञानिक', 'तथ्य',
    'अनुसंधान', 'अध्ययन', 'विशेषज्ञ'
]

ENGLISH_REFUTING_WORDS = [
    'false', 'fake', 'hoax', 'debunked', 'disproven', 'myth', 'untrue',
    'misleading', 'misinformation', 'fact-check reveals false', 'not true',
    'fabricated', 'baseless', 'unfounded', 'incorrect', 'wrong',
    'conspiracy theory', 'no evidence', 'lacks evidence', 'unproven',
    'rating: false', 'mostly false', 'pants on fire', 'fiction'
]

ENGLISH_SUPPORTING_WORDS = [
    'confirmed', 'verified', 'proven', 'true', 'accurate', 'correct',
    'evidence shows', 'research confirms', 'studies prove', 'data shows',
    'scientists confirm', 'experts verify', 'officially confirmed',
    'rating: true', 'mostly true', 'legitimate', 'substantiated'
]

# Devanagari characters for language detection
NEPALI_CHARS = [
    'क', 'ख', 'ग', 'घ', 'ङ', 'च', 'छ', 'ज', 'झ', 'ञ', 
    'ट', 'ठ', 'ड', 'ढ', 'ण', 'त', 'थ', 'द', 'ध', 'न', 
    'प', 'फ', 'ब', 'भ', 'म', 'य', 'र', 'ल', 'व', 'श', 
    'ष', 'स', 'ह', 'ा', 'ि', 'ी', 'ु', 'ू', 'े', 'ै', 
    'ो', 'ौ', '्'
]

# Add these missing constants
HIGH_CREDIBILITY_DOMAINS = [
    'reuters.com', 'ap.org', 'bbc.com', 'cnn.com', 'nytimes.com',
    'washingtonpost.com', 'npr.org', 'pbs.org', 'factcheck.org',
    'snopes.com', 'politifact.com', 'ekantipur.com', 'kathmandupost.com',
    'theguardian.com', 'economist.com', 'wsj.com'
]

MEDIUM_CREDIBILITY_DOMAINS = [
    'forbes.com', 'time.com', 'newsweek.com', 'guardian.com',
    'independent.co.uk', 'onlinekhabar.com', 'setopati.com',
    'usatoday.com', 'cbsnews.com', 'nbcnews.com'
]

LOW_CREDIBILITY_DOMAINS = [
    'facebook.com', 'twitter.com', 'youtube.com', 'instagram.com',
    'tiktok.com', 'whatsapp.com', 'infowars.com', 'breitbart.com'
]

# Search query templates
FACT_CHECK_QUERIES = {
    'en': [
        'fact check {}',
        '{} debunked',
        '{} true or false',
        '{} verified',
        'is {} real'
    ],
    'ne': [
        '{} तथ्य परीक्षण',
        '{} सत्य कि झूटो',
        '{} भ्रामक',
        '{} पुष्टि'
    ],
    'hi': [
        '{} तथ्य जांच',
        '{} सच या झूठ',
        '{} भ्रामक',
        '{} सत्यापन'
    ]
}