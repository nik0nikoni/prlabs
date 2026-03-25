import httpx


class TodoApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self._client = httpx.AsyncClient(timeout=5.0)

    async def close(self):
        await self._client.aclose()


    # ____________READ___________
    async def get_tasks(self):
        r = await self._client.get(f'{self.base_url}/tasks')
        r.raise_for_status()
        return r.json()
    
    async def get_task(self, task_id: int):
        r =  await self._client.get(f'{self.base_url}/tasks/{task_id}')
        r.raise_for_status()
        return r.json()
    

    # ___________________CREATE_________________
    async def create_task(self, title: str, description: str = ''):
        r = await self._client.post(
            f'{self.base_url}/tasks',
            json={
                'title': title,
                'description': description,
            },
        )
        r.raise_for_status()
        return r.json()
    

    # ____________UPDATE_____________
    async def update_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        is_done: bool | None = None,
    ):
        payload = {}
        if title is not None:
            payload['title'] = title
        if description is not None:
            payload['description'] = description
        if is_done is not None:
            payload['is_done'] = is_done
        
        r = await self._client.put(
            f'{self.base_url}/tasks/{task_id}',
            json=payload
        )
        r.raise_for_status()
        return r.json()
    

    #_______________DELETE____________________
    async def delete_task(self, task_id: int):
        r = await self._client.delete(f'{self.base_url}/tasks/{task_id}')
        
        if r.status_code == 204:
            return True

        if r.status_code == 404:
            return False
        
        
        r.raise_for_status()
        return False
    
    # ================= EMAIL: SMTP =================
    async def send_mail(self, to: str, subject: str, body: str):
        r = await self._client.post(
            f'{self.base_url}/email/send',
            json={
                'to': to,
                'subject': subject,
                'body': body,
            }
        )
        r.raise_for_status()
        return r.json()