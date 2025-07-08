from config import SERVICE_ACCOUNT_PATH, PROJECT_ID, DATASET_NAME, TABLE_NAME
from core.bigquery import BigQueryClient
from repository.bigquery_league_repo import LeagueRepository
from repository.bigquery_match_repo import MatchRepository
from repository.bigquery_user_repo import UserRepository
from repository.bigquery_url_submission_repo import UrlSubmissionRepository
from repository.gcs_file_repo import GCSFileRepository
from service.league_svc import LeagueSvc
from service.match_svc import MatchSvc
from service.login_svc import LoginSvc
from service.user_svc import UserSvc
from service.url_submission_svc import UrlSubmissionSvc
from service.file_upload_svc import FileUploadSvc

## bigquery client init
get_bigquery_client=None
try:
    # Init bigquery client
    bqclient = BigQueryClient(SERVICE_ACCOUNT_PATH, PROJECT_ID)
    get_bigquery_client = bqclient.get_bigquery_client
    bqClient_init = True
except:
    bqClient_init = False

if get_bigquery_client:
    try:
        # Init user repo
        user_repo = UserRepository(get_bigquery_client(), PROJECT_ID, DATASET_NAME, TABLE_NAME)
        # Init login service
        login_svc = LoginSvc(user_repo)
        # Init user service
        user_svc = UserSvc(user_repo)
    except:
        user_svc = None
        login_svc = None

    try:
        # Init league repo
        league_repo = LeagueRepository(get_bigquery_client(), PROJECT_ID, DATASET_NAME, "leagues")
        # Init league service
        league_svc = LeagueSvc(league_repo)
    except:
        league_svc = None
    
    try:
        # Init match repo
        match_repo = MatchRepository(get_bigquery_client(), PROJECT_ID, DATASET_NAME, table_name="matches", league_table_name="leagues")
        # Init match service
        match_svc = MatchSvc(match_repo)
    except:
        match_svc = None

    try:
        # Init url submission repo
        url_submission_repo = UrlSubmissionRepository(get_bigquery_client(), PROJECT_ID, DATASET_NAME, "url_submission")
        # Init url submission service
        url_submission_svc = UrlSubmissionSvc(url_submission_repo)
    except:
        url_submission_svc = None

    try:
        # Init GCS file repo
        gcs_file_repo = GCSFileRepository(bucket_name="web_anti", project_id=PROJECT_ID)
        # Init file upload service
        file_upload_svc = FileUploadSvc(gcs_file_repo)
    except:
        file_upload_svc = None