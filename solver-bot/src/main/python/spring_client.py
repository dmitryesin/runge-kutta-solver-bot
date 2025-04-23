import numpy as np
import asyncio
import json

from aiohttp import ClientError, ClientTimeout, ClientSession
from equation.function_replacer import replace_math_functions

JAVA_SERVER_URL = "http://localhost:8080/api/solver"
REQUEST_TIMEOUT = 60 
MAX_RETRIES = 3
RETRY_DELAY = 1

async def set_parameters(
    user_id, method, order, user_equation, formatted_equation,
    initial_x, initial_y, reach_point, step_size
):
    method_mapping = {
        "method_euler": 1,
        "method_modified_euler": 2,
        "method_runge_kutta": 4,
        "method_dormand_prince": 7
    }

    payload = {
        "method": method_mapping.get(method, 1),
        "order": int(order),
        "userEquation": user_equation,
        "formattedEquation": replace_math_functions(formatted_equation),
        "initialX": float(initial_x),
        "initialY": list(map(float, initial_y.split())),
        "reachPoint": float(reach_point),
        "stepSize": float(step_size)
    }

    for attempt in range(MAX_RETRIES):
        try:
            timeout = ClientTimeout(total=REQUEST_TIMEOUT)
            async with ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{JAVA_SERVER_URL}/solve/{user_id}",
                    json=payload
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except (ClientError, asyncio.TimeoutError) as e:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
                continue
            raise e


async def set_user_settings(user_id, language, rounding, method):
    payload = {
        "language": language,
        "rounding": rounding,
        "method": method
    }

    timeout = ClientTimeout(total=REQUEST_TIMEOUT)
    async with ClientSession(timeout=timeout) as session:
        async with session.post(
            f"{JAVA_SERVER_URL}/user-settings/{user_id}",
            params=payload
        ) as response:
            response.raise_for_status()
            return await response.text()


async def get_user_settings(user_id, language, rounding, method):
    timeout = ClientTimeout(total=REQUEST_TIMEOUT)
    async with ClientSession(timeout=timeout) as session:
        async with session.get(
            f"{JAVA_SERVER_URL}/user-settings/{user_id}"
        ) as response:
            if response.status == 500:
                return {
                    'method': method,
                    'rounding': rounding,
                    'language': language
                }

            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                return await response.json()
            else:
                text = await response.text()
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return text


async def get_recent_applications(user_id):
    timeout = ClientTimeout(total=REQUEST_TIMEOUT)
    async with ClientSession(timeout=timeout) as session:
        async with session.get(
            f"{JAVA_SERVER_URL}/application/list/{user_id}"
        ) as response:
            if response.status == 500:
                return []
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                data = await response.json()
            else:
                text = await response.text()
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    return []

            valid_statuses = {"new", "in_progress", "completed"}

            filtered = []

            if isinstance(data, list):
                for app in data:
                    if isinstance(app, dict) and app.get("status") in valid_statuses:
                        filtered.append(app)
                        if len(filtered) == 5:
                            break
                return filtered

            elif isinstance(data, dict) and 'applications' in data:
                applications = data['applications']
                if isinstance(applications, list):
                    for app in applications:
                        if isinstance(app, dict) and app.get("status") in valid_statuses:
                            filtered.append(app.get('id') if 'id' in app else app)
                            if len(filtered) == 5:
                                break
                    return filtered

            return []


async def get_solution(application_id):
    timeout = ClientTimeout(total=REQUEST_TIMEOUT)
    async with ClientSession(timeout=timeout) as session:
        async with session.get(
            f"{JAVA_SERVER_URL}/solution/{application_id}"
        ) as response:
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                data = await response.json()
            else:
                text = await response.text()
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    raise ValueError(f"Failed to parse solution data: {text}")
            return np.array(data)


async def get_x_values(application_id):
    timeout = ClientTimeout(total=REQUEST_TIMEOUT)
    async with ClientSession(timeout=timeout) as session:
        async with session.get(
            f"{JAVA_SERVER_URL}/x-values/{application_id}"
        ) as response:
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                data = await response.json()
            else:
                text = await response.text()
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    raise ValueError(f"Failed to parse x-values data: {text}")
            return np.array(data)


async def get_y_values(application_id):
    timeout = ClientTimeout(total=REQUEST_TIMEOUT)
    async with ClientSession(timeout=timeout) as session:
        async with session.get(
            f"{JAVA_SERVER_URL}/y-values/{application_id}"
        ) as response:
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                data = await response.json()
            else:
                text = await response.text()
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    raise ValueError(f"Failed to parse y-values data: {text}")
            return np.array(data)


async def get_application_status(application_id):
    timeout = ClientTimeout(total=REQUEST_TIMEOUT)
    async with ClientSession(timeout=timeout) as session:
        async with session.get(
            f"{JAVA_SERVER_URL}/application/{application_id}/status"
        ) as response:
            response.raise_for_status()
            return await response.text()


async def wait_for_application_completion(application_id):
    request_limit = REQUEST_TIMEOUT
    for _ in range(request_limit):
        try:
            status = await get_application_status(application_id)
            if status == "completed":
                return True
            elif status == "in_progress":
                request_limit += 1
                if request_limit > REQUEST_TIMEOUT * 2:
                    return False
            elif status == "error":
                return False
            await asyncio.sleep(RETRY_DELAY)
        except Exception:
            await asyncio.sleep(RETRY_DELAY)
    
    return False
