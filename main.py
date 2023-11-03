import os
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery

# Function to authenticate the user and save credentials to a file
def authenticate():
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "client_secrets.json", scopes
    )
    credentials = flow.run_local_server(port=0)

    # Save credentials to a file
    with open("credentials.pkl", "wb") as token:
        pickle.dump(credentials, token)

    print("Authentication successful. Credentials saved to 'credentials.pkl'.")

# Function to create a YouTube playlist and add videos from the file
def create_youtube_playlist(playlist_name, video_file_path):
    # Load credentials from a file
    if os.path.exists("credentials.pkl"):
        with open("credentials.pkl", "rb") as token:
            credentials = pickle.load(token)
    else:
        print("Error: Please run 'text2ytpl login' to authenticate first.")
        return

    # Initialize YouTube Data API v3 service
    api_service_name = "youtube"
    api_version = "v3"
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

    # Create a new YouTube playlist
    request = youtube.playlists().insert(
        part="snippet",
        body={
            "snippet": {
                "title": playlist_name,
                "description": "Playlist created by text2ytpl command-line tool.",
            }
        },
    )
    response = request.execute()
    playlist_id = response["id"]

    # Read video URLs from the file and add them to the playlist
    with open(video_file_path, "r") as file:
        video_urls = file.readlines()

    for video_url in video_urls:
        # Extract video ID from the URL
        video_id = video_url.strip().split("v=")[1]

        # Add video to the playlist
        request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        )
        request.execute()

    print(f"Playlist '{playlist_name}' created successfully with {len(video_urls)} videos.")

# Command-line interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create YouTube playlist and add videos.")
    subparsers = parser.add_subparsers(dest="command")

    # Subparser for the 'login' command
    login_parser = subparsers.add_parser("login", help="Start authentication flow.")

    # Subparser for the 'import' command
    import_parser = subparsers.add_parser("import", help="Create playlist and import videos.")
    import_parser.add_argument("playlist_name", help="Name of the YouTube playlist")
    import_parser.add_argument("video_file_path", help="Path to the file containing video URLs")

    args = parser.parse_args()

    if args.command == "login":
        authenticate()
    elif args.command == "import":
        create_youtube_playlist(args.playlist_name, args.video_file_path)
