# Changelog

## v1.2.8 (in progress)

- Added: Queries that are missing a citation number now show a friendly error message instead of causing a JSON parse failure in the backend.
- Added: Citations with a null totalDueAmt are now gracefully treated as ineligible instead of raising an internal error.
- Both of the above changes will result in fewer error e-mails going to the support address.
- Fixed bug introduced with name search in v1.2.7
- Added: You can now select "I don't have proof available" even for "other" type benefits.

## v1.2.7 ([2019-10-22](d7215a9b150a7a992df15f0ae0dc44a45ceefeec))

- Changed: queries to ATP API now send the date in YYYY-MM-DD format. This fixes a bug when querying the San Francisco API.

## v1.2.6 ([2019-10-11](d05dc98d6d8458889e808531943ae7ae8d71fe3c))

- Changed: Spanish translation of intro page text
- Changed: Log API request info even if the request fails
- Added: Track clicks on language select dropdown in GA
- Changed: "Try again in 24 hours" -> "Try again later" during an error

## v1.2.5 ([2019-10-01](7d1e45ad0e4b58f6a155e37a1d31126ff1ca46ab))

- Changed: Spanish translation of intro page text

## v1.2.4 ([2019-09-25](9a17fc4078f6e4be26a9049822e7ad0de7b17b69))

- Changed: higher-resolution translation icon (for high-res screens)

## v1.2.3 ([2019-09-24](9a17fc4078f6e4be26a9049822e7ad0de7b17b69))

### User-facing changes

- Changed: Improved mobile layout (full-width buttons, no horizontal scroll).
- Added: The proof of benefits questions now have form validation.
- Added: Maximum 300 character limit on answer to other financial hardship question.
- Added: Text for free-response questions in Spanish indicating that answers must be in English.
- Changed: Intro page text.
- Changed: Expect a response from the court by email in **30** business days (instead of 10).

## v1.2.0 (unreleased)

### User-facing changes

- Added: Language dropdown now appears in the upper right, with options for both Spanish and English versions! Woohoo!
- Removed: "Necesita español?" button no longer needed now that we have the Spanish language version.
- Changed: When querying for a citation number, the user is now presented with the specific citation that they searched for *in addition to* every citation under their name in the selected county!
- Changed: Users are now able to select *more than one* citation from the list of citation results and submit fine reduction requests for all citations at once!

### Under-the-hood changes

- Added: An e-mail now gets sent to the ATP support e-mail address whenever the application experiences a problem communicating with the ATP API (e.g. if the API times out or returns an HTTP error response).
- Changed: Better error logging in general, so support can easily debug when issues arise.
- Changed: Refactored code so it is easier to understand and maintain in the future.

## v1.1.0 ([2019-08-23](https://github.com/JudicialCouncilOfCalifornia/docassemble.jcc.abilitytopay/commit/716cc36c5d708b54e20ed1cde6c7465fdf868436))

### User-facing changes

- Added: Ventura now appears in the county dropdown! Welcome, Ventura county!
- Added: If the user searches for an ambiguous citation number that corresponds to more than one citation (e.g. because the citation number from an earlier active case has been reused by the court), they are taken directly to a name search form. (Before this release, it was not possible for the UI to receive multiple citations corresponding to a single citation number because the ATP API was programmed to only ever send back one citation even when multiple were found.)

### Under-the-hood changes

- Changed: The application now expects to always receive a *list* datatype of citations from the ATP API instead of a single citation object.
- Added: Now sending race and zip code information, if present, with each fine reduction request.
