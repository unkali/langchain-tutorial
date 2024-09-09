from operator import itemgetter

from dotenv import load_dotenv
from langchain.chains.sql_database.query import _strip
from langchain_aws import ChatBedrockConverse
from langchain_community.tools import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tracers import ConsoleCallbackHandler

# Load environment variables from .env
load_dotenv()

# connect to the database
mysql_uri = 'mysql+mysqlconnector://root:test@localhost:59235/test'
#  db name is test which is running on docker (Deals-API)

db = SQLDatabase.from_uri(mysql_uri)
print(db.dialect)
print(db.get_usable_table_names())
print(db.get_table_info())


llm = ChatBedrockConverse(
    model="anthropic.claude-3-5-sonnet-20240620-v1:0",
    temperature=0,
    max_tokens=None,
    # other params...
)

PROMPT_SUFFIX = """Only use the following tables:
{table_info}

Question: {input}"""

_DEFAULT_TEMPLATE = """You are an expert in GraphQL and SQL queries who understands the following GraphQL schema
{gqlSchema}.

Given a GraphQL query from the above schema, create a syntactically correct MySQL query to run, then look at the results of the query and return the answer

Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.

Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.

Use the following format:

Question: Question here
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here

"""

PROMPT = PromptTemplate(
    input_variables=["input", "table_info", "dialect", "gqlSchema"],
    template=_DEFAULT_TEMPLATE + PROMPT_SUFFIX,
)

graphql_schema = """
type Query {
  # Get a TripleLift Deal.
  deal(input: DealInput!): DealInternal
  
  # Returns a list of supported targets based on the input
  targets(input: TargetGroupInput!): [Target!]!
}

input DealInput {
  dealId: Long!
  # This will filter out any deals that are not valid for an auction in the Exchange
  validForAuction: Boolean @deprecated
  performanceInput: PerformanceInput @deprecated
}

input DealsInput {
  dealIds: [Long!]! @ContainerSize(min: 1, max: 10)
}

input CopyDealInput {
  dealId: Long! @Positive
}

input SetDealGoalsInput {
  dealId: Long!
  primaryGoalId: Int @Positive
  secondaryGoalId: Int @Positive
}

input SetDealSpendTypeInput {
  dealId: Long! @Positive
  dealSpendTypeId: Int @Positive
}

input SetDealDiscountInput {
  dealId: Long! @Positive
  discount: BigDecimal @Positive
}

input SetDealTypeInput {
  dealId: Long! @Positive
  dealTypeId: Int @Positive
}

input DealQueryInput {
  name: String
  dealIds: [Long!]
  active: Boolean
  deleted: Boolean
  dealTypeId: Int
    @deprecated(
      reason: "Use the dealTypeIds field instead. Any input value on this field will be ignored"
    )
  dealTypeIds: [Int!]
  formatTargetIds: [Int!]
  memberIds: [Int!]
  # The TP Id to filter by (multiple deals can have the same TP)
  targetingProfileId: Long
  # The AQP Id to filter by (multiple deals can have the same AQP)
  adQualityProfileId: Long
  # This will filter out any deals that are not valid for an auction in the Exchange
  # If validForAuction==true then the active and deleted flags are ignored.
  validForAuction: Boolean
  performanceInput: PerformanceInput
}

type DealInternal {
  id: Long!
  active: Boolean
  deleted: Boolean
  name: String!
  code: String!
  memberId: Int!
  anId: BigInteger
  lastModified: DateTime
  lastModifiedUserId: Int
    @deprecated(
      reason: "Use `lastModifiedByUserId` instead which supports Auth0 users as well"
    )
  lastModifiedByUserId: String
  createdByUserId: String
  isPmp: Boolean @deprecated
  bidFloor: BigDecimal
  margin: BigDecimal
  priority: Int
  adQualityProfile: AdQualityProfile
  targetingProfile: TargetingProfile
  # ISO 8601 Date format 'yyyy-MM-dd'
  startDate: Date
  # ISO 8601 Date format 'yyyy-MM-dd'
  endDate: Date
  openAuction: Boolean
  # An RFC-3339 compliant date time like '2020-03-12T16:00:00Z'.
  timeCreated: DateTime
  dealTypeId: Int
  budget: BigDecimal
  discount: BigDecimal
  impressionVolume: BigInteger
  isMarketplace: Boolean
  primaryGoalId: Int
  secondaryGoalId: Int @deprecated(reason: "Use secondaryGoal")
  dealSpendTypeId: Int
  ceilingDollarsCpm: BigDecimal
  competitiveSeparationEnabled: Boolean
  dealSubType: DealSubType
  dealPriceType: DealPriceType
  dealStatus: DealStatus
  performance: PerformanceResponseData
  secondaryGoal: SecondaryGoal
}

type SecondaryGoal {
  id: Int
  value: SecondaryGoalValue
}

type SecondaryGoalValue {
  value: BigDecimal!
  type: SecondaryGoalValueType!
}

enum SecondaryGoalValueType {
  USD_CENTS
  BIG_INTEGER
  PERCENTAGE
}

type DealInternalConnection implements Connection {
  edges: [DealInternalEdge!]!
  pageInfo: PageInfo
}

type DealInternalEdge implements Edge {
  node: DealInternal
  cursor: String
}
enum TargetGroup {
  BROWSER
  CONTENT_CATEGORY
  DEVICE
  FORMAT
  INVENTORY_TYPE
  LANGUAGE
  OS
  SUPPLY_SOURCE
  GEO_DMA
  GEO_REGION
  GEO_COUNTRY
  GEO_SECTOR
  RENDER_OPTION
  EXTERNAL_CREATIVE_TYPE
  DOMAIN_CATEGORY
  JOUNCE_SPO_SEGMENT
}

input TargetGroupInput {
  targetGroup: TargetGroup!
  active: Boolean
  deleted: Boolean
}

union Target =
    BrowserTarget
  | ContentCategoryTarget
  | DeviceTarget
  | FormatTarget
  | InventoryTypeTarget
  | LanguageTarget
  | OsTarget
  | SupplySourceTarget
  | GeoTarget
  | RenderOptionTarget
  | ExternalCreativeTypeTarget
  | DomainCategoryTarget
  | JounceSpoSegmentTarget

type BrowserTarget {
  id: Int!
  name: String!
  optionId: Int!
}

type ContentCategoryTarget {
  id: Int!
  name: String
  visible: Boolean
  lastUpdated: DateTime
  iabCode: String
  deleted: Boolean
}

type DeviceTarget {
  id: Int!
  type: String!
  name: String!
}

type FormatTarget {
  id: Int!
  code: String!
  name: String!
  active: Boolean!
  margin: BigDecimal!
  uiVisibilityOptions: String
  deletedAt: DateTime
  createdAt: DateTime
  updatedAt: DateTime
}

type InventoryTypeTarget {
  id: Int!
  name: String
}

type LanguageTarget {
  id: Int!
  code: String!
  name: String!
}

type OsTarget {
  id: Int!
  name: String
  optionId: Int!
}

type SupplySourceTarget {
  id: Int!
  name: String
}

type GeoTarget {
  id: Int!
  name: String
  code: String
  geoType: GeoType!
  # For some reason, the generated code in DGS has the field _parent instead of parent
  parent: String
}

enum GeoType {
  COUNTRY
  REGION
  SECTOR
  DMA
}

type RenderOptionTarget {
  id: Int!
  code: String!
  name: String!
  deleted: Boolean!
}

type ExternalCreativeTypeTarget {
  id: Int!
  externalCreativeTypeName: String
  connectionTypeName: String
}

type DomainCategoryTarget {
  id: Int!
  name: String
  domains: [Domain!]
}

type Domain {
  id: Int!
  domainName: String
  useSubdomain: Boolean
  usePlacementUrl: Boolean
}

type JounceSpoSegmentTarget {
  id: Int!
  name: String
}

input ContentCategoryTargetInput {
  id: Int!
  name: String
  visible: Boolean
  lastUpdated: DateTime
  iabCode: String
  deleted: Boolean
}

"""

execute_query = QuerySQLDataBaseTool(db=db)

inputs = {
    "input": lambda x: x["question"] + "\nSQLQuery: ",
    "table_info": lambda x: db.get_table_info(
        table_names=x.get("table_names_to_use")
    ),
}

write_query = (
        RunnablePassthrough.assign(**inputs)  # type: ignore
        | (
            lambda x: {
                k: v
                for k, v in x.items()
                if k not in ("question", "table_names_to_use")
            }
        )
        | PROMPT
        | llm.bind(stop=["\nSQLResult:"])
        | StrOutputParser()
        | _strip
    )

answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: 

Make sure the answer follows the GraphQL response spec"""
)

chain = (
    RunnablePassthrough.assign(query=write_query).assign(
        result=itemgetter("query") | execute_query
    )
    | answer_prompt
    | llm
    | StrOutputParser()
)

my_input = {
    "question": """
        query{
          targets(input: {
            targetGroup: GEO_COUNTRY
          }) {
            __typename
            ... on GeoTarget {
              id
              name
              code
            geoType
              parent
            }
          }
        }
    
    Only return the SQL without any other text or explanation
    """,
    "gqlSchema": graphql_schema
}

# ConsoleCallbackHandler helps us print output of every step of the chain to console
response = chain.invoke(my_input, config={'callbacks': [ConsoleCallbackHandler()]})
print(response)

