# Travel Agency API

Run the API from the project root with either of these commands:

```bash
uv run uvicorn app.main:app --reload
```

or:

```bash
uv run uvicorn main:app --reload
```

`main.app:app` is not a valid import path in this repository.

## Environment Configuration

Create a `.env` file inside the `travel-agency-api/` directory.

Example:

```env
RAPIDAPI_KEY=your_rapidapi_key_here

CORS_ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:5173
CORS_ALLOW_CREDENTIALS=true
```

### Notes

- Replace `your_rapidapi_key_here` with your personal RapidAPI key.
- Multiple CORS origins should be comma-separated.
- Do not commit `.env` files to git.
- Restart the backend server after updating environment variables.