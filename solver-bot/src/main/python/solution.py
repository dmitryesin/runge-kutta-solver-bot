import numpy as np
import asyncio
import json

from aiohttp import ClientError, ClientTimeout, ClientSession
from equation.function_replacer import replace_math_functions

JAVA_SERVER_URL = "http://localhost:8080/api/solver"
REQUEST_TIMEOUT = 60 
MAX_RETRIES = 3
RETRY_DELAY = 1

async def set_java_parameters(user_id, method, order, equation, initial_x, initial_y, reach_point, step_size):
    method_mapping = {
        "method_euler": 1,
        "method_modified_euler": 2,
        "method_runge_kutta": 4,
        "method_dormand_prince": 7
    }

    payload = {
        "method": method_mapping.get(method, 1),
        "order": int(order),
        "equation": replace_math_functions(equation),
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


async def get_user_settings(user_id):
    timeout = ClientTimeout(total=REQUEST_TIMEOUT)
    async with ClientSession(timeout=timeout) as session:
        async with session.get(
            f"{JAVA_SERVER_URL}/user-settings/{user_id}"
        ) as response:
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


async def get_application_status(application_id):
    timeout = ClientTimeout(total=REQUEST_TIMEOUT)
    async with ClientSession(timeout=timeout) as session:
        async with session.get(
            f"{JAVA_SERVER_URL}/application/{application_id}/status"
        ) as response:
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


async def get_application_creation_date(application_id):
    timeout = ClientTimeout(total=REQUEST_TIMEOUT)
    async with ClientSession(timeout=timeout) as session:
        async with session.get(
            f"{JAVA_SERVER_URL}/application/{application_id}/creation_date"
        ) as response:
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

            if isinstance(data, list):
                return data[:5]
            elif isinstance(data, dict) and 'applications' in data:
                applications = data['applications']
                if isinstance(applications, list):
                    if applications and isinstance(applications[0], dict) and 'id' in applications[0]:
                        return [app['id'] for app in applications[:5]]
                    return applications[:5]

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


async def wait_for_application_completion(application_id, max_attempts=60, delay=1):
    for _ in range(max_attempts):
        try:
            status = await get_application_status(application_id)
            if status == "completed":
                return True
            elif status == "error":
                return False
            await asyncio.sleep(delay)
        except Exception as e:
            await asyncio.sleep(delay)
    
    return False


def get_result_info(result, order, rounding):
    try:
        order = int(order)
    except ValueError:
        return ""

    superscripts = "⁰¹²³⁴⁵⁶⁷⁸⁹"

    def get_variable_name(i):
        if i < 4:
            return f"y{chr(39) * i}"
        return f"y{"⁽"}{''.join(superscripts[int(d)] for d in str(i))}{"⁾"}"

    result_str = f"x: {result[0]:.2f}"
    variable_names = ["y"] + [get_variable_name(i) for i in range(1, int(order))]

    for i in range(1, order + 1):
        if i < len(result):
            result_str += f", {variable_names[i-1]}: {result[i]:.{rounding}f}"
        else:
            result_str += f", {variable_names[i-1]}: NaN"

    return result_str
