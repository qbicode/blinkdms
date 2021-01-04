BlinkDMS
========

BlinkDMS is a lightweight DMS (Document Management System) for small companies (~500 employees) or other organizations. 
It is focused on version management and a controlled release process.


Features:
  * target area: industrial research, development, production
  * max number of documents or versions: just limited by the memory volume, designed for millions of docs
  * typical number of users: 100, but theoretically unlimited (some GUI elements will be improved for larger numbers in the future)
  * area of usage: cooperation, workflow, regulated doc archiving, need for released documents
  * special scope: regulated (medical) industries under e.g. ISO13485, FDA CFR820, ready for software validation (not included in the documentation)
  * electronic signature support, if configured: password validation required in the approval process
  * each document has an unique, configurable document ID
  * optional automatic conversion from word to PDF, including document-ID, title and approval data injection
  * separate working areas for released and unreleased documents, no hassle with retrieving unreleased docs
  * possible to integrate with other systems
  * time of system implementation: install 2h; configuration: 10 minutes
  * mobile support
  * work offline: NO
  * multi language support: currently NO, TODO
  
Difference to other DMS systems:
  * designed for the usage in a (medical) regulated environment (ISO13485, FDA CFR820)
  * documents are organized in a flexible folder system, so people find documents in an intuitive way
  * strict separation of the working area of released documents and documents under construction


Future features:
  * Edit workflow
  * REST interface
  * make GUI ready for unlimited number of users
  
Demo
----

A demo is available at http://www.blinkdms.org:8080/

Following initial users are available:
  * testW: jajsxB8738  (normal editor, reviewer)
  * testX: kskxny537WtqtzwP$s  (normal editor, reviewer)
  * testY: aPllqwbxnfhfzre52Ms (normal editor, reviewer)
  * testZ: ldlMmsh62Ds9ahUiu+dx (can only VIEW)

Links
-----

 * Website:  http://www.blinkdms.org
 * Tutorial: https://qbicode.github.io/blinkdms/
 * Install:  https://qbicode.github.io/blinkdms/
 * Demo: http://www.blinkdms.org:8080/
 
 Support
 -------
 
 This project is supported by   `Bling AG <https://www.blink-dx.com>`_ .

