Database tables
###############

Tables content at install
*************************

What data is need at initial DUMP import:
  * GLOBALS
  * CCT_TABLE
  * CCT_COLUMN
  * WFL     (the default workflows)
  * DB_USER (at least account for root)
  * STATE



WFL (workflow type)
*******************

Scope: define the type of workflow, is linked to a document type

Types:
  * NO_WFL  :no workflow needed
  * REL_ONLY : only release
  * REV_REL : REVIEW + RELEASE
  
Type==REL_ONLY :
  * the document needs only users for RELEASE
  
  
Type==REV_REL :
  * the document needs users for REVIEW + RELEASE
  
Type==NO_WFL :
  * the document needs no reviewers
  * the document will be released on workflow start
  



