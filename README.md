# nc-backup: Naver Cafe Backup Tool

네이버 카페에 작성한 게시물 및 첨부파일을 백업할 수 있는 도구입니다.  
현재 네이버 카페는 본인이 작성한 게시물을 백업하는 기능을 제공하고 있지 않습니다만, 본 프로그램을 사용하면 본문과 함께 사진, 영상, 첨부파일을 일괄적으로 백업할 수 있습니다.

## 특징
* 본인이 작성한 게시물을 모두 백업하거나, 게시물 번호를 하나 이상 지정하여 선택적으로 백업할 수 있습니다.
* 백업할 게시물을 직접 선택하는 경우, 본인이 열람할 수 있는 게시물이라면 직접 작성하지 않았더라도 백업이 가능합니다.
* 본문은 pdf 파일로 저장되며, 애셋(사진, 동영상, 첨부파일 등)은 별도의 폴더에 다운로드됩니다.

## 사용법
작성 예정

## 주의사항
* 네이버 카페 사이트 구조가 변경될 시, 본 프로그램이 제대로 작동하지 않을 수 있습니다. 2024.04 기준으로 정상 작동을 확인했습니다. 오작동 시 Issues 혹은 메일로 제보 바랍니다.
* 기본적으로 크롤링을 이용하므로, 트래픽에 부하를 줄 정도의 과도한 사용은 자제해 주시기 바랍니다.

## 참고사항
Selenium을 사용하여 개발하였으며, 프로그램의 기본적인 틀은 [wjdgowns77/NaverCafeBackupProject](https://github.com/wjdgowns77/NaverCafeBackupProject) 프로젝트를 참고했음을 밝힙니다.