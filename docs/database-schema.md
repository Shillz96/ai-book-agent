# Conceptual Database Schema: Firestore

This document outlines a conceptual Firestore database schema for the AI Book Marketing Agent.

## Global Variables
- **__app_id**: Current application ID.
- **__firebase_config**: Firebase project configuration.
- **__initial_auth_token**: Firebase custom authentication token.

## Top-Level Collections
- **Public Data**: `/artifacts/{appId}/public/data/{collection_name}`
- **Private Data**: `/artifacts/{appId}/users/{userId}/{collection_name}`

## Proposed Collections and Document Structures

### 1. `userSettings` Collection
- **Purpose**: Stores user-specific configurations.
- **Document ID**: `settings`
- **Fields**:
  - `bookTitle`: String
  - `bookAuthor`: String
  - `amazonLink`: String
  - `audibleLink`: String
  - `landingPageUrl`: String
  - `googleAnalyticsId`: String
  - `googleAdsCustomerId`: String
  - `monthlyBudget`: Number
  - `budgetAllocationRules`: Map
  - `contentGuidelines`: String
  - `socialMediaAccounts`: Map
  - `humanInLoopEnabled`: Boolean
  - `lastUpdated`: Timestamp

### 2. `campaigns` Collection
- **Purpose**: Stores details of marketing campaigns.
- **Document ID**: Auto-generated
- **Fields**:
  - `name`: String
  - `type`: String
  - `status`: String
  - `platformId`: String
  - `startDate`: Timestamp
  - `endDate`: Timestamp
  - `budget`: Number
  - `currentSpend`: Number
  - `targeting`: Map
  - `aiNotes`: String
  - `lastModifiedBy`: String
  - `createdAt`: Timestamp
  - `updatedAt`: Timestamp

### 3. `posts` Collection
- **Purpose**: Stores details of social media posts.
- **Document ID**: Auto-generated
- **Fields**:
  - `campaignId`: String
  - `platform`: String
  - `content`: String
  - `mediaUrl`: String
  - `hashtags`: Array
  - `status`: String
  - `scheduledTime`: Timestamp
  - `publishedTime`: Timestamp
  - `platformPostId`: String
  - `aiGenerated`: Boolean
  - `aiRationale`: String
  - `humanApproved`: Boolean
  - `humanFeedback`: String
  - `performanceMetrics`: Map
  - `createdAt`: Timestamp
  - `updatedAt`: Timestamp

### 4. `ads` Collection
- **Purpose**: Stores details of individual ad creatives.
- **Document ID**: Auto-generated
- **Fields**:
  - `campaignId`: String
  - `adGroupId`: String
  - `platform`: String
  - `type`: String
  - `headline1`: String
  - `headline2`: String
  - `description1`: String
  - `finalUrl`: String
  - `status`: String
  - `platformAdId`: String
  - `aiGenerated`: Boolean
  - `aiRationale`: String
  - `humanApproved`: Boolean
  - `humanFeedback`: String
  - `performanceMetrics`: Map
  - `createdAt`: Timestamp
  - `updatedAt`: Timestamp

### 5. `performanceMetrics` Collection
- **Purpose**: Stores aggregated daily/weekly performance data.
- **Document ID**: Auto-generated
- **Fields**:
  - `date`: Timestamp
  - `platform`: String
  - `metricType`: String
  - `data`: Map
  - `createdAt`: Timestamp

### 6. `reports` Collection
- **Purpose**: Stores generated weekly performance reports.
- **Document ID**: Auto-generated
- **Fields**:
  - `reportDate`: Timestamp
  - `summary`: String
  - `actionsTaken`: String
  - `resultsAchieved`: String
  - `insightsLearned`: String
  - `recommendations`: String
  - `rawMetricsSnapshot`: Map
  - `createdAt`: Timestamp

## Data Serialization
For complex objects or arrays, consider storing them as JSON strings to manage Firestore's limitations on deeply nested structures. 