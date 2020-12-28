Technologies
============

Convert Word 2 PDF
------------------

Requirements on the document:

* one word file as attachment on the document
* the word file containes some KEYWORDS which will be replaced automatically

Process:

* take the word file
* do DocReplaceText() for title, doc code, version, ...
* produce a temp word file (TMP.docx)
* produce a final PDF file (set UPLOADS.HAS_PDF=1 for this upload)
* save PDF as oDOC.{VERSION}.{POS}.pdf

Relevant code modules:

* lib/oVERSION/docfile_convert.py (converts a version attachment)