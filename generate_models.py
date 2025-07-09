import openai
import argparse
import os

def generate_likec4_model(prompts, api_key):
    """
    Generates a C4 model in LikeC4 DSL format using OpenAI's API.

    Args:
        prompts (list): A list of strings describing the system.
        api_key (str): Your OpenAI API key.

    Returns:
        str: The generated C4 model in LikeC4 DSL format, or an error message.
    """
    if not api_key:
        return "Error: OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."

    openai.api_key = api_key

    # Updated, more robust prompt to enforce best practices and avoid common modeling errors.
    instruction_prompt = """
You are a world-class expert in software architecture, domain-driven design, and the LikeC4 DSL. Your primary task is to generate a valid, detailed, and architecturally sound C4 model based on the user's description.

The output MUST be a single, complete code block in the LikeC4 DSL format. Adhere strictly to the following structure and rules:

**Core Rules:**
1.  **`specification` block**: Always begin with this block. Define all element kinds used: `actor`, `softwareSystem`, `container`, `component`, and `externalSystem`.
2.  **`model` block**:
    * **Element Naming:** Use short, consistent `camelCase` identifiers for all elements (e.g., `webApp`, `apiGateway`).
    * **Element Definitions:** Define all people (`actor`), software systems (`softwareSystem`), and external systems (`externalSystem`).
    * **Container vs. Component:** This is critical.
        * A `container` is a deployable, runnable unit. This includes applications (Web Apps, APIs, microservices) AND data stores (Databases, Caches, Message Queues like Redis). **Data stores are ALWAYS containers.**
        * A `component` is an internal part of a container, like a code module or a group of classes (e.g., 'JWT Issuer' inside an 'Authentication Service'). Do not model separate infrastructure as components.
    * **Rich Detail:** Provide detailed `description` and `technology` tags for every single element.
    * **Specific Relationships:** Relationships (`->`) MUST be between the most specific elements possible.
        * **NEVER** link from a `softwareSystem` to an `externalSystem`. Instead, link from the specific `container` within the system that makes the call (e.g., `quantumLeap.apiGateway -> stripe`).
        * Use active and descriptive labels for relationships (e.g., 'Sends GraphQL requests to', 'Reads/writes user data from/to').

3.  **`views` block**:
    * Create a `view index` for the System Landscape.
    * For EACH `softwareSystem`, create a `view containers of ...` to show its internal structure.
    * For any `container` that has `component` elements, create a `view components of ...`.
    * Use `autoLayout` and `style` blocks to create clean, readable diagrams.

**A Gold-Standard Example to Follow:**

```likec4
specification {
  element actor
  element softwareSystem
  element container
  element component
  element externalSystem
}

model {
  dataAnalyst = actor 'Data Analyst' {
    description 'Builds and runs data models to gain insights.'
  }

  quantumLeap = softwareSystem 'QuantumLeap Analytics' {
    tags 'saas'
    description 'A multi-tenant SaaS platform for data analytics.'

    webApp = container 'Web App' {
      technology 'React, TypeScript'
      description 'The main user interface for data analysts to interact with the platform.'
    }

    apiGateway = container 'API Gateway' {
      technology 'Node.js, Apollo GraphQL'
      description 'Single entry point for all client requests. Routes traffic to backend services.'
    }

    authService = container 'Authentication Service' {
      technology 'Go'
      description 'Handles user identity, authentication, and permissions.'

      jwtIssuer = component 'JWT Issuer' {
        description 'Issues and validates JSON Web Tokens for secure sessions.'
      }
    }

    // CORRECT: Redis is modeled as its own container, not a component.
    redisQueue = container 'Redis Job Queue' {
      technology 'Redis'
      description 'Queue for job management, ensuring reliable scheduling and execution.'
    }

    postgresDB = container 'PostgreSQL Database' {
      technology 'PostgreSQL'
      description 'Stores user data, permissions, and metadata about data models.'
    }
  }

  stripe = externalSystem 'Stripe' {
    description 'Handles customer subscriptions and payments.'
  }

  // Relationships
  dataAnalyst -> quantumLeap.webApp 'Uses'
  quantumLeap.webApp -> quantumLeap.apiGateway 'Sends GraphQL requests to'
  quantumLeap.authService -> quantumLeap.postgresDB 'Reads/writes user data from/to'

  // CORRECT: Relationship is from a specific container, not the whole system.
  quantumLeap.apiGateway -> stripe 'Processes payments through'
}

views {
  view index {
    title "System Landscape for QuantumLeap Analytics"
    include *
    autoLayout TopBottom
  }

  view containers of quantumLeap {
    title "Container Diagram for QuantumLeap Analytics"
    include *, quantumLeap.*
    autoLayout LeftRight
  }

  view components of quantumLeap.authService {
    title "Component Diagram for Authentication Service"
    include *, quantumLeap.authService.*
    autoLayout TopBottom
  }

  style * {
    color secondary
  }
  style quantumLeap {
    color primary
  }
  style dataAnalyst {
    color actor
  }
  style stripe {
    color muted
  }
}
```

Now, based on the following description, create a detailed C4 model using the LikeC4 DSL:
"""

    # Combine the instruction prompt with the user's specific prompts
    full_prompt = instruction_prompt + "\n\n" + "\n".join(prompts)

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in software architecture and the LikeC4 DSL. Your task is to generate valid, complex, and detailed LikeC4 code."},
                {"role": "user", "content": full_prompt}
            ]
        )
        
        c4_code = response.choices[0].message.content.strip()
        
        # Clean up the response to remove markdown code block fences if they exist
        if c4_code.startswith("```likec4"):
            c4_code = c4_code[len("```likec4"):].strip()
        if c4_code.startswith("```"):
            c4_code = c4_code[len("```"):].strip()
        if c4_code.endswith("```"):
            c4_code = c4_code[:-len("```")].strip()

        # Basic validation for the LikeC4 format
        if 'model {' in c4_code and 'views {' in c4_code and 'specification {' in c4_code:
            return c4_code
        else:
            return f"Error: The model did not return valid LikeC4 code. Please check the response:\n{c4_code}"

    except openai.APIError as e:
        return f"Error: OpenAI API returned an API Error: {e}"
    except openai.APIConnectionError as e:
        return f"Error: Failed to connect to OpenAI API: {e}"
    except openai.RateLimitError as e:
        return f"Error: OpenAI API request exceeded rate limit: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def save_to_file(content, filename):
    """Saves the given content to a file, creating the directory if it doesn't exist."""
    try:
        # Ensure the directory exists before writing the file
        output_dir = os.path.dirname(filename)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        if not filename.endswith('.c4'):
            filename += '.c4'
            
        with open(filename, 'w') as f:
            f.write(content)
        print(f"Successfully saved LikeC4 model to {filename}")
    except IOError as e:
        print(f"Error: Could not write to file {filename}. Reason: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a C4 model file for the LikeC4 extension using OpenAI."
    )
    parser.add_argument(
        "prompts",
        metavar="PROMPT",
        type=str,
        nargs='+',
        help="One or more descriptive prompts to generate the C4 model from."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="generated_model.c4",
        help="The name of the output .c4 file. Defaults to 'generated_model.c4'."
    )

    args = parser.parse_args()
    #api_key = os.getenv("OPENAI_API_KEY")
    api_key = os.getenv("OPENAI_API_KEY")

    print("Generating LikeC4 model from your prompts...")
    c4_model_code = generate_likec4_model(args.prompts, api_key)

    if c4_model_code and not c4_model_code.startswith("Error"):
        # Save file to the specified path, creating 'src' if needed.
        output_path = os.path.join("src", args.output)
        save_to_file(c4_model_code, output_path)
    else:
        print(c4_model_code)
