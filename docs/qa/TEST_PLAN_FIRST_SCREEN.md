# Test Plan: Main Screen (Stocks/ETF Ranking)

## Objective
Verify the correct functionality of the main screen displaying stocks/ETF ranking based on real backend data.

## Test Scope
- Data presentation (symbol, name, AI score, 1M return, trend, country/category)
- UI interactions (search, section switching, pagination)
- Error handling and edge cases
- Responsiveness and accessibility
- Performance and loading states
- Data validation and formatting

## Business Requirements Mapping

### Core Features (Based on Mockup Specification)
- Display ranked list of stocks and ETFs by AI score
- Show company symbol, name, AI score, 1M return, and trend indicators
- Support both stocks (with country badges) and ETFs (with category badges)
- Visual indicators: AI score badges with color coding, return percentages with color coding, trend arrows

## Detailed Test Scenarios

### 1. Data Display and Presentation
**Test ID: TD-001**
- **Objective**: Verify correct data display on application startup
- **Steps**:
  1. Launch application
  2. Verify both "Top Stocks" and "Top ETFs" tables are displayed
  3. Verify table headers are correct
  4. Verify each row contains all required fields
- **Expected Result**: Both tables load with complete data structure
- **Priority**: High

**Test ID: TD-002**
- **Objective**: Verify AI Score badge color coding
- **Steps**:
  1. Examine AI scores in both tables
  2. Verify color coding: Score ≥9 (green), 7-8 (yellow), 5-6 (orange), <5 (red)
- **Expected Result**: All scores display correct colors
- **Priority**: High

**Test ID: TD-003**
- **Objective**: Verify return percentage color coding and formatting
- **Steps**:
  1. Check 1M return values
  2. Verify positive returns show in green with "+" prefix
  3. Verify negative returns show in red
  4. Verify formatting to 2 decimal places
- **Expected Result**: Correct color coding and formatting
- **Priority**: High

**Test ID: TD-004**
- **Objective**: Verify trend indicators
- **Steps**:
  1. Check change values and corresponding arrows
  2. Verify: positive change (↑, green), negative change (↓, red), no change (→, gray)
- **Expected Result**: Correct arrows and colors for all entries
- **Priority**: High

### 2. Data Validation and Edge Cases
**Test ID: DV-001**
- **Objective**: Test with extreme AI score values
- **Steps**:
  1. Test with AI scores: 0, 1, 5, 7, 9, 10
  2. Verify correct badge colors for each range
- **Expected Result**: Appropriate color coding for all score ranges
- **Priority**: Medium

**Test ID: DV-002**
- **Objective**: Test with extreme return values
- **Steps**:
  1. Test with returns: -99.99%, 0%, +999.99%
  2. Verify formatting and color coding
- **Expected Result**: Correct display for extreme values
- **Priority**: Medium

**Test ID: DV-003**
- **Objective**: Test with long company names
- **Steps**:
  1. Test display with very long company names (>50 characters)
  2. Verify text wrapping or truncation
- **Expected Result**: Names display without breaking layout
- **Priority**: Low

### 3. Loading States and Performance
**Test ID: LS-001**
- **Objective**: Verify loading indicators (addressing identified gap)
- **Steps**:
  1. Simulate slow API response
  2. Verify loading indicator is shown
  3. Verify content appears after loading completes
- **Expected Result**: Loading indicator shown during data fetch
- **Priority**: High

**Test ID: LS-002**
- **Objective**: Test API timeout handling
- **Steps**:
  1. Simulate API timeout
  2. Verify appropriate error message is displayed
- **Expected Result**: User-friendly timeout message
- **Priority**: Medium

### 4. Empty State Handling
**Test ID: ES-001**
- **Objective**: Test empty data scenarios (addressing identified gap)
- **Steps**:
  1. Mock empty API response for stocks
  2. Mock empty API response for ETFs
  3. Verify appropriate "no data" messages
- **Expected Result**: Clear "no data available" messages
- **Priority**: Medium

### 5. Responsiveness Testing
**Test ID: RT-001**
- **Objective**: Verify mobile responsiveness
- **Steps**:
  1. Test on mobile viewport (320px-768px)
  2. Verify tables are readable and scrollable
  3. Verify proper spacing and touch targets
- **Expected Result**: Usable interface on mobile devices
- **Priority**: High

**Test ID: RT-002**
- **Objective**: Verify tablet responsiveness
- **Steps**:
  1. Test on tablet viewport (768px-1024px)
  2. Verify layout adaptation
- **Expected Result**: Optimal layout for tablet screens
- **Priority**: Medium

**Test ID: RT-003**
- **Objective**: Verify desktop layout
- **Steps**:
  1. Test on desktop viewport (>1024px)
  2. Verify side-by-side table layout
- **Expected Result**: Tables displayed side by side
- **Priority**: High

### 6. Accessibility Testing
**Test ID: AT-001**
- **Objective**: Keyboard navigation testing
- **Steps**:
  1. Navigate entire interface using only keyboard
  2. Verify all interactive elements are reachable
  3. Verify proper tab order
- **Expected Result**: Full keyboard accessibility
- **Priority**: High

**Test ID: AT-002**
- **Objective**: Screen reader compatibility (addressing identified gap)
- **Steps**:
  1. Test with screen reader software
  2. Verify table headers are properly announced
  3. Verify data relationships are clear
- **Expected Result**: Screen reader announces content correctly
- **Priority**: Medium

**Test ID: AT-003**
- **Objective**: Color contrast validation
- **Steps**:
  1. Verify all text meets WCAG AA standards
  2. Test badge colors for sufficient contrast
- **Expected Result**: All content meets accessibility standards
- **Priority**: Medium

### 7. Content Accuracy and Consistency
**Test ID: CA-001**
- **Objective**: Verify data consistency between tables
- **Steps**:
  1. Check that ranking numbers are sequential
  2. Verify date consistency in both tables
- **Expected Result**: Consistent ranking and dates
- **Priority**: Medium

**Test ID: CA-002**
- **Objective**: Verify descriptive text accuracy
- **Steps**:
  1. Verify explanation text matches functionality
  2. Check date format and current date display
- **Expected Result**: Accurate and current information
- **Priority**: Low

### 8. User Interface Elements
**Test ID: UI-001**
- **Objective**: Verify main title and header display
- **Steps**:
  1. Check that main title displays "Popular Stocks Ranked by AI"
  2. Verify subtitle with date information is present
  3. Verify proper centering and styling of header elements
- **Expected Result**: Header displays correctly with proper formatting
- **Priority**: Medium

**Test ID: UI-002**
- **Objective**: Verify grid layout behavior across devices
- **Steps**:
  1. Test desktop layout (>1024px) shows tables side-by-side
  2. Test tablet layout (768px-1024px) shows appropriate adaptation
  3. Test mobile layout (<768px) shows single column
- **Expected Result**: Grid layout responds appropriately to screen size
- **Priority**: High

### 9. Future Interactive Elements
**Test ID: FI-001**
- **Objective**: Test "Show ETFs" button functionality (when implemented)
- **Steps**:
  1. Locate "Show ETFs" button in interface
  2. Click button and verify view changes
  3. Test button state and visual feedback
- **Expected Result**: Button correctly toggles to ETF-focused view
- **Priority**: High (when feature exists)

**Test ID: FI-002**
- **Objective**: Test "Show More" button functionality (when implemented)
- **Steps**:
  1. Locate "Show More" button in interface
  2. Click button and verify additional data loads
  3. Test pagination or data expansion behavior
- **Expected Result**: More data loads without breaking layout
- **Priority**: High (when feature exists)

## Future Enhancement Test Cases

### Search Functionality (When Implemented)
**Test ID: SF-001**
- **Objective**: Test search functionality
- **Steps**:
  1. Enter symbol in search box
  2. Enter company name in search box
  3. Test partial matches
  4. Test case insensitive search
- **Expected Result**: Accurate filtering of results
- **Priority**: High (when feature exists)

**Test ID: SF-002**
- **Objective**: Test empty search results (addressing identified gap)
- **Steps**:
  1. Enter non-existent symbol
  2. Verify "no results found" message
- **Expected Result**: Clear "no results" message
- **Priority**: Medium (when feature exists)

### Sorting Functionality (When Implemented)
**Test ID: ST-001**
- **Objective**: Test column sorting (addressing identified gap)
- **Steps**:
  1. Click on sortable column headers
  2. Verify ascending/descending sort
  3. Test sort indicators
- **Expected Result**: Correct sorting behavior
- **Priority**: Medium (when feature exists)

## Automation Strategy

### Unit Tests
- Component rendering tests
- Data formatting function tests
- Color coding logic tests
- Badge component tests

### Integration Tests
- API integration tests with mock data
- Component interaction tests
- State management tests

### E2E Tests
- Full user journey tests
- Cross-browser compatibility
- Performance benchmarks
- Accessibility compliance

### Visual Regression Tests
- Screenshot comparisons
- Layout consistency checks
- Color accuracy validation

## Test Data Requirements

### Valid Test Data
- Stocks with various AI scores (1-10)
- Returns ranging from -50% to +100%
- Different country codes
- Various ETF categories
- Mix of positive, negative, and zero changes

### Edge Case Data
- Extreme return values
- Maximum length company names
- Minimum/maximum AI scores
- Empty/null values handling

## Success Criteria

### Functional Requirements
- ✅ All data displays correctly
- ✅ Color coding works as specified
- ✅ Layout is responsive across devices
- ✅ Accessibility standards are met
- ✅ Loading states are handled
- ✅ Error conditions are handled gracefully

### Performance Requirements
- Initial load time < 3 seconds
- Smooth interactions on mobile devices
- No layout shifts during data loading

### Accessibility Requirements
- WCAG AA compliance
- Screen reader compatibility
- Keyboard navigation support
- Adequate color contrast ratios

## Notes
- Tests should use realistic financial data for accuracy
- Consider internationalization requirements for future releases
- Monitor for potential new features mentioned in product specifications
- Regular review and update of test cases as product evolves
