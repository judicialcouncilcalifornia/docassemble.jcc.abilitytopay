# Changelog

## v1.2.1 (unreleased)

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
