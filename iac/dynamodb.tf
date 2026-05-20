resource "aws_dynamodb_table" "c23_epipelagic_public_figures" {
  name           = "c23-epipelagic-dynamo-public-figures"
  billing_mode   = "PAY_PER_REQUEST" # On-demand capacity (cost-effective for starters)
  hash_key       = "PK" # Will hold PublicFigureID (e.g., "PF_001")
  range_key      = "SK"  # Will hold "METADATA" OR "ARTICLE#Timestamp#TitleSlug"

  # You must declare the attributes that are used as keys
  attribute {
    name = "PK"
    type = "S" # S = String
  }

  attribute {
    name = "SK"
    type = "S"
  }

  attribute {
    name = "NormalisedName"
    type = "S"
  }

  # Defining the Global Secondary Index
  global_secondary_index {
    name               = "NormalisedNameIndex"
    key_schema {
      attribute_name = "NormalisedName"
      key_type = "HASH"
    }
    projection_type    = "ALL" # Copies all attributes to the GSI. (Can change to KEYS_ONLY or INCLUDE)
  }

  tags = {
    Environment = "Production"
    Project     = "C23EpipelagicDashboard"
  }
}