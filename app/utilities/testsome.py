# First, import your required libraries and any necessary parts of your script
import asyncio
from ..repositories.mlRepository import mlRepository  # Make sure to adjust this import according to your actual file structure.

# Create an instance of the repository
repo = mlRepository()

# Define a small async function to run your fetchData method
async def run_fetch():
    return await repo.fetchData(6, '2020-10-05','2020-10-10')  # Adjust parameters as needed

# Run the event loop
df = asyncio.run(run_fetch())
print(df)