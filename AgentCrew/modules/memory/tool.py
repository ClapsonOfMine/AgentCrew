from typing import Dict, Any, Callable

from AgentCrew.modules.agents import AgentManager
from .base_service import BaseMemoryService


def get_memory_forget_tool_definition(provider="claude") -> Dict[str, Any]:
    """
    Get the enhanced tool definition for forgetting memories based on provider.

    This tool provides comprehensive memory management capabilities for AI agents,
    allowing them to strategically remove irrelevant, outdated, or conflicting
    information from their memory systems.

    Args:
        provider: The LLM provider ("claude" or "groq")

    Returns:
        Dict containing the enhanced tool definition with comprehensive descriptions
    """
    tool_description = """Strategically removes memories related to specific topics from conversation history and long-term storage. 

    **PRIMARY USE CASES:**
    • Clearing sensitive or personal information that should not be retained
    • Removing outdated information that conflicts with newer, accurate data
    • Eliminating irrelevant details that may cause confusion in future interactions
    • Correcting factual errors by removing incorrect memories before storing updated information
    • Managing memory storage efficiency by pruning unnecessary historical data

    **STRATEGIC CONSIDERATIONS:**
    • Use sparingly to preserve valuable context and learning patterns
    • Always provide clear justification for memory removal decisions
    • Consider the impact on future conversation continuity
    • Prefer targeted removal using specific IDs when possible to minimize context loss
    
    **ERROR PREVENTION:**
    • Verify topic keywords are specific enough to avoid over-deletion
    • Use memory IDs for precise removal when available
    • Document the reason for removal in your response to maintain transparency"""

    tool_arguments = {
        "topic": {
            "type": "string",
            "description": """Keywords describing the specific topic or domain to be forgotten. 
            
            **BEST PRACTICES:**
            • Use precise, descriptive terms to avoid over-broad deletion
            • Include context-specific identifiers (dates, names, project codes)
            • Combine multiple related keywords with spaces for broader matching
            • Consider semantic variations and synonyms of the target topic
            
            **EXAMPLES:**
            • "project_alpha_2024_credentials" - for specific project security data
            • "outdated_api_documentation_v1" - for deprecated technical information  
            • "user_personal_contact_details" - for privacy-sensitive information
            • "incorrect_financial_calculations_march" - for erroneous data correction
            
            **AVOID:**
            • Overly broad terms like "user" or "project" that might delete valuable context
            • Single-character or very short keywords that could match unintended content""",
        },
        "ids": {
            "type": "array",
            "items": {"type": "string"},
            "description": """Optional list of specific memory entry IDs for surgical removal of targeted memories.
            
            **WHEN TO USE IDS:**
            • When you have exact memory identifiers from previous retrieval operations
            • For precise removal of specific conversation segments or knowledge entries
            • To avoid collateral deletion of related but valuable memories
            • When topic-based removal might be too broad or imprecise
            
            **ID FORMAT EXPECTATIONS:**
            • Alphanumeric strings, UUIDs, or system-generated identifiers
            • Multiple IDs can be provided for batch operations
            • IDs take precedence over topic-based removal when both are provided
            
            **SAFETY FEATURES:**
            • Only specified IDs will be removed, providing maximum precision
            • Failed ID removals will be reported without affecting other operations
            • Invalid IDs are ignored with appropriate error messaging""",
        },
    }
    tool_required = ["topic"]

    if provider == "claude":
        return {
            "name": "forget_memory_topic",
            "description": tool_description,
            "input_schema": {
                "type": "object",
                "properties": tool_arguments,
                "required": tool_required,
            },
        }
    else:  # provider == "groq"
        return {
            "type": "function",
            "function": {
                "name": "forget_memory_topic",
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_arguments,
                    "required": tool_required,
                },
            },
        }


def get_memory_forget_tool_handler(memory_service: BaseMemoryService) -> Callable:
    """
    Get the enhanced handler function for the memory forget tool with comprehensive error handling.

    Args:
        memory_service: The memory service instance

    Returns:
        Function that handles memory forgetting requests with detailed feedback
    """

    def handle_memory_forget(**params) -> str:
        topic = params.get("topic")
        ids = params.get("ids", [])

        try:
            current_agent = AgentManager.get_instance().get_current_agent()
            agent_name = current_agent.name if current_agent else "unknown_agent"
        except Exception as e:
            return f"Error: Unable to identify current agent for memory operation: {str(e)}"

        # Prioritize ID-based removal for precision
        if len(ids) > 0:
            try:
                result = memory_service.forget_ids(ids, agent_name)
                if result["success"]:
                    return f"✅ Successfully removed {len(ids)} specific memory entries: {result['message']}"
                else:
                    return f"⚠️ Partial or failed memory removal: {result.get('message', 'Unknown error occurred')}"
            except Exception as e:
                return f"❌ Error during ID-based memory removal: {str(e)}. Please verify the memory IDs are valid and try again."

        # Topic-based removal with enhanced validation
        if not topic or not topic.strip():
            return "❌ Error: Topic is required for memory removal. Please provide specific keywords describing what should be forgotten."

        # Validate topic is not too broad or risky
        risky_keywords = ["all", "everything", "user", "conversation", "memory"]
        if topic.lower().strip() in risky_keywords:
            return f"⚠️ Warning: The keyword '{topic}' is too broad and could remove valuable context. Please use more specific terms."

        try:
            result = memory_service.forget_topic(topic, agent_name)
            if result["success"]:
                return f"✅ Successfully removed memories related to '{topic}': {result['message']}"
            else:
                return f"⚠️ Memory removal incomplete: {result.get('message', 'Unknown error occurred')}. Some memories may not have been found or removed."
        except Exception as e:
            return f"❌ Error removing memories for topic '{topic}': {str(e)}. Please check the topic keywords and try again."

    return handle_memory_forget


def get_memory_retrieve_tool_definition(provider="claude") -> Dict[str, Any]:
    """
    Get the enhanced tool definition for retrieving memories based on provider.

    This tool provides sophisticated semantic search capabilities for accessing
    relevant historical information and contextual knowledge from past interactions.

    Args:
        provider: The LLM provider ("claude" or "groq")

    Returns:
        Dict containing the enhanced tool definition with comprehensive guidance
    """
    tool_description = """Retrieves contextually relevant information from conversation history and stored knowledge using advanced semantic search.

    **PRIMARY STRATEGIC APPLICATIONS:**
    • **Context Enrichment**: Gather relevant background from previous conversations before responding
    • **Knowledge Continuity**: Access established facts, preferences, and patterns from past interactions  
    • **Decision Support**: Retrieve historical decisions and their outcomes for informed current choices
    • **Relationship Building**: Access user preferences, communication styles, and personal context
    • **Problem Solving**: Find similar past issues and their resolutions for pattern-based solutions

    **OPTIMAL USAGE PATTERNS:**
    • **Conversation Startup**: ALWAYS retrieve context at the beginning of new conversations
    • **Topic Transitions**: Search for relevant background when user changes subjects
    • **Complex Queries**: Gather comprehensive context before providing detailed responses
    • **Follow-up Actions**: Access previous action items, commitments, or ongoing projects
    • **Personalization**: Retrieve user preferences and communication patterns for tailored responses

    **SEARCH OPTIMIZATION STRATEGIES:**
    • Use specific, descriptive keywords rather than generic terms
    • Combine multiple concepts with spaces for broader semantic matching
    • Include temporal indicators (recent, last week, previous project) when relevant
    • Consider synonyms and related terminology for comprehensive coverage
    • Balance specificity with breadth based on the information need"""

    tool_arguments = {
        "keywords": {
            "type": "string",
            "description": """Semantic search terms optimized for retrieving the most relevant memories and context.

            **KEYWORD OPTIMIZATION TECHNIQUES:**
            
            **SPECIFIC SEARCHES** (for targeted information):
            • "project_alpha_api_integration" - for specific project technical details
            • "user_preferences_communication_style" - for personalization context
            • "previous_error_database_connection" - for technical problem-solving
            • "meeting_notes_client_requirements_2024" - for business context
            
            **BROAD SEARCHES** (for general context):
            • "user goals objectives priorities" - for understanding user intentions
            • "recent conversations important decisions" - for ongoing context
            • "technical challenges solutions patterns" - for problem-solving approaches
            • "feedback preferences suggestions improvements" - for service enhancement
            
            **TEMPORAL SEARCHES** (for time-based context):
            • "recent updates changes modifications" - for latest developments
            • "historical patterns trends behaviors" - for long-term analysis
            • "last conversation session interaction" - for immediate context
            
            **MULTI-CONCEPT SEARCHES** (for complex topics):
            • "authentication security implementation best practices" - combining related concepts
            • "user interface design feedback usability testing" - for comprehensive UI context
            • "performance optimization database queries caching" - for technical architecture
            
            **SEMANTIC CONSIDERATIONS:**
            • The system uses embedding-based similarity matching, not exact keyword matching
            • Related concepts and synonyms will be found even if not explicitly mentioned
            • Context and meaning matter more than exact word matching
            • Longer, more descriptive phrases often yield better results than single words""",
        },
        "limit": {
            "type": "integer",
            "default": 5,
            "description": """Maximum number of memory entries to retrieve, with strategic sizing recommendations.

            **LIMIT SIZING STRATEGY:**
            
            **Small Searches (1-3 items):**
            • Quick fact-checking or specific information lookup
            • When you need just the most relevant single piece of information
            • For simple yes/no questions or basic preference checks
            
            **Medium Searches (4-7 items):** [DEFAULT - RECOMMENDED]
            • Standard context gathering for most conversations
            • Balanced view of relevant information without overwhelming detail
            • Suitable for most topic transitions and response preparation
            
            **Large Searches (8-15 items):**
            • Comprehensive context for complex decision-making
            • When starting work on multifaceted projects or problems
            • For detailed analysis requiring broad historical perspective
            • When user asks for thorough background or comprehensive review
            
            **PERFORMANCE CONSIDERATIONS:**
            • Larger limits provide more context but may include less relevant results
            • Processing time increases with larger result sets
            • Consider the complexity of your task when choosing the limit
            • Start with default (5) and adjust based on information sufficiency""",
        },
    }
    tool_required = ["keywords"]

    if provider == "claude":
        return {
            "name": "retrieve_memory",
            "description": tool_description,
            "input_schema": {
                "type": "object",
                "properties": tool_arguments,
                "required": tool_required,
            },
        }
    else:  # provider == "groq"
        return {
            "type": "function",
            "function": {
                "name": "retrieve_memory",
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_arguments,
                    "required": tool_required,
                },
            },
        }


def memory_instruction_prompt():
    """
    Enhanced memory system instruction prompt with comprehensive strategic guidance.

    Returns:
        Comprehensive instruction prompt for memory system usage
    """
    return """<Memory_System>
  <Purpose>
    Advanced contextual enrichment system that maintains conversation continuity, preserves important knowledge, 
    and enables intelligent information management across interactions. The memory system serves as the foundation 
    for building long-term relationships and maintaining consistent, personalized user experiences.
  </Purpose>

  <Strategic_Framework>
    <Context_Enrichment>
      Proactively retrieve relevant background information to enhance response quality and maintain conversation flow.
      Always prioritize context gathering before providing substantive responses to complex queries.
    </Context_Enrichment>
    
    <Knowledge_Continuity>
      Maintain persistent awareness of user preferences, past decisions, ongoing projects, and established facts
      to provide consistent and personalized assistance across multiple interactions.
    </Knowledge_Continuity>
    
    <Information_Lifecycle_Management>
      Strategically manage the creation, retrieval, update, and removal of memories to maintain accurate,
      relevant, and useful information while preventing context pollution and information conflicts.
    </Information_Lifecycle_Management>
  </Strategic_Framework>

  <Operational_Guidelines>
    <Memory_Retrieval_Strategies>
      <Primary_Triggers>
        • **Conversation Initiation**: ALWAYS retrieve context at the start of new conversations or sessions
        • **Topic_Transitions**: Search for relevant background when user introduces new subjects or changes focus
        • **Complex_Queries**: Gather comprehensive context before responding to multi-faceted or detailed requests
        • **Follow_Up_Requests**: Access previous interactions when user references past conversations or commitments
        • **Decision_Support**: Retrieve historical patterns and outcomes when user needs guidance or recommendations
      </Primary_Triggers>
      
      <Search_Optimization>
        • Use specific, descriptive keywords that capture the essence of needed information
        • Combine multiple concepts for broader semantic coverage while maintaining relevance
        • Include temporal indicators (recent, previous, last meeting) when time context matters
        • Balance specificity with breadth based on the complexity of the information need
        • Consider synonyms and related terminology to ensure comprehensive coverage
      </Search_Optimization>
      
      <Result_Processing>
        • Analyze retrieved memories for relevance and accuracy before incorporating into responses
        • Synthesize information from multiple memory sources to provide coherent, comprehensive context
        • Identify gaps in retrieved information that might require additional searches or clarification
        • Use memory insights to personalize responses and maintain consistent interaction patterns
      </Result_Processing>
    </Memory_Retrieval_Strategies>

    <Memory_Management_Protocols>
      <Forget_Memory_Applications>
        • **Accuracy_Maintenance**: Remove outdated or incorrect information when more accurate data becomes available
        • **Privacy_Protection**: Delete sensitive personal information when requested or when retention is inappropriate
        • **Conflict_Resolution**: Clear conflicting memories that might cause confusion in future interactions
        • **Storage_Optimization**: Remove irrelevant or redundant information to maintain system efficiency
        • **User_Corrections**: Eliminate incorrect facts immediately when user provides corrections or clarifications
      </Forget_Memory_Applications>
      
      <Removal_Safety_Protocols>
        • Always provide clear justification for memory removal decisions
        • Use specific memory IDs when available for precise, surgical removal
        • Verify topic keywords are sufficiently specific to avoid over-deletion
        • Document the removal reason to maintain transparency and accountability
        • Consider the impact on conversation continuity before removing established context
      </Removal_Safety_Protocols>
    </Memory_Management_Protocols>
  </Operational_Guidelines>

  <Quality_Assurance>
    <Memory_Validation>
      Regularly verify that retrieved memories are still accurate, relevant, and beneficial to current interactions.
      Cross-reference new information with existing memories to identify potential conflicts or updates needed.
    </Memory_Validation>
    
    <Performance_Monitoring>
      Track the effectiveness of memory operations in improving conversation quality and user satisfaction.
      Adjust search strategies and memory management approaches based on successful interaction patterns.
    </Performance_Monitoring>
    
    <Continuous_Improvement>
      Learn from memory usage patterns to optimize future retrieval strategies and information organization.
      Refine memory management decisions based on user feedback and interaction outcomes.
    </Continuous_Improvement>
  </Quality_Assurance>

  <Error_Handling_And_Recovery>
    <Graceful_Degradation>
      When memory operations fail, continue with available context while informing user of limitations.
      Provide alternative approaches for information gathering when memory systems are unavailable.
    </Graceful_Degradation>
    
    <Error_Communication>
      Clearly communicate memory operation results, including partial failures or unexpected outcomes.
      Offer specific guidance for resolving memory-related issues or limitations.
    </Error_Communication>
    
    <Fallback_Strategies>
      Maintain conversation quality even when memory operations encounter problems.
      Use conversation history and contextual clues as backup sources of relevant information.
    </Fallback_Strategies>
  </Error_Handling_And_Recovery>
</Memory_System>"""


def get_memory_retrieve_tool_handler(memory_service: BaseMemoryService) -> Callable:
    """
    Get the enhanced handler function for the memory retrieve tool with comprehensive error handling.

    Args:
        memory_service: The memory service instance

    Returns:
        Function that handles memory retrieval requests with detailed feedback and optimization
    """

    def handle_memory_retrieve(**params) -> str:
        keywords = params.get("keywords")
        limit = params.get("limit", 5)

        # Enhanced agent identification with fallback
        try:
            current_agent = AgentManager.get_instance().get_current_agent()
            agent_name = current_agent.name
        except Exception:
            agent_name = ""  # Graceful fallback for system operations

        # Input validation with helpful error messages
        if not keywords or not keywords.strip():
            return "❌ Error: Search keywords are required for memory retrieval. Please provide specific terms describing the information you're looking for."

        # Keyword optimization suggestions
        if len(keywords.strip()) < 3:
            return f"⚠️ Warning: Search term '{keywords}' may be too short for effective semantic search. Consider using more descriptive keywords for better results."

        # Limit validation and optimization
        if limit < 1:
            limit = 1
        elif limit > 50:  # Reasonable upper bound to prevent performance issues
            limit = 50

        try:
            result = memory_service.retrieve_memory(keywords, limit, agent_name)

            # Enhanced result processing and feedback
            if not result or result.strip() == "":
                return f"📝 No memories found matching '{keywords}'. Consider:\n• Using broader or alternative keywords\n• Checking if the information was previously stored\n• Trying related terms or synonyms"

            # Count retrieved memories for user feedback
            memory_count = result.count("\n---") + 1 if "---" in result else 1
            if memory_count < limit:
                feedback_prefix = f"📚 Retrieved {memory_count} relevant memories (requested {limit}): "
            else:
                feedback_prefix = f"📚 Retrieved {memory_count} memories: "

            return f"{feedback_prefix}\n\n{result}"

        except Exception as e:
            return f"❌ Error retrieving memories for '{keywords}': {str(e)}. Please try rephrasing your search terms or contact support if the issue persists."

    return handle_memory_retrieve


def get_adapt_tool_definition(provider="claude") -> Dict[str, Any]:
    """
    Get the enhanced tool definition for adaptive behavior management based on provider.

    This tool enables AI agents to learn and adapt their behavior patterns based on
    user interactions, preferences, and successful interaction patterns.

    Args:
        provider: The LLM provider ("claude" or "groq")

    Returns:
        Dict containing the enhanced tool definition with comprehensive adaptation guidance
    """
    tool_description = """Stores and manages adaptive behavioral patterns that enhance user experience through personalized interaction approaches.

    **ADAPTIVE BEHAVIOR PHILOSOPHY:**
    Adaptive behaviors allow AI agents to learn from successful interactions and automatically
    apply personalized approaches in future conversations. These behaviors create consistency,
    improve user satisfaction, and build more effective long-term relationships.

    **PRIMARY ADAPTATION CATEGORIES:**

    **Communication Style Adaptations:**
    • Response length preferences (detailed vs. concise)
    • Technical depth adjustments (expert vs. beginner explanations)
    • Formality levels (professional vs. casual interaction styles)
    • Information presentation formats (lists, paragraphs, step-by-step)

    **Task Execution Adaptations:**
    • Problem-solving approaches preferred by the user
    • Code review and documentation standards
    • Meeting and deadline management preferences
    • Error handling and troubleshooting methodologies

    **Context-Aware Adaptations:**
    • Domain-specific expertise applications (finance, healthcare, education)
    • Seasonal or time-sensitive behavior modifications
    • Project-specific workflow optimizations
    • Collaborative interaction patterns with team members

    **Learning-Based Adaptations:**
    • User correction patterns leading to improved accuracy
    • Feedback-driven service improvements
    • Successful interaction pattern recognition and replication
    • Failed approach identification and avoidance strategies

    **IMPLEMENTATION STRATEGY:**
    Use the 'when...do...' format to create clear, actionable behavioral triggers that can be
    automatically activated based on conversation context and user interaction patterns."""

    tool_arguments = {
        "id": {
            "type": "string",
            "description": """Unique identifier for the adaptive behavior, designed for easy management and updates.

            **ID NAMING CONVENTIONS:**
            
            **Category-Based IDs** (recommended structure):
            • "communication_style_[aspect]" - for interaction preferences
            • "task_execution_[domain]" - for work approach patterns  
            • "error_handling_[context]" - for problem-solving behaviors
            • "personalization_[area]" - for user-specific customizations
            
            **SPECIFIC EXAMPLES:**
            • "communication_style_technical_depth" - for adjusting explanation complexity
            • "task_execution_code_review" - for code analysis and feedback approaches
            • "error_handling_database_issues" - for specific technical problem domains
            • "personalization_meeting_scheduling" - for calendar and time management
            • "feedback_integration_documentation" - for how to handle user corrections
            • "collaboration_style_team_projects" - for multi-person interaction patterns
            
            **ID BEST PRACTICES:**
            • Use lowercase with underscores for consistency
            • Include domain/context for easy categorization
            • Make IDs descriptive enough to understand without reading the behavior
            • Group related behaviors with consistent prefixes
            • Keep IDs concise but meaningful (aim for 2-4 components)
            
            **UPDATE STRATEGY:**
            • Use existing IDs to update/refine behaviors based on new interactions
            • Create new IDs for genuinely different behavioral patterns
            • Archive obsolete behaviors by updating them with new patterns""",
        },
        "behavior": {
            "type": "string",
            "description": """The behavioral pattern description using the mandatory 'when...do...' conditional format.

            **BEHAVIOR STRUCTURE REQUIREMENTS:**
            All behaviors MUST follow the format: "when [trigger condition] do [specific action]"

            **EFFECTIVE TRIGGER CONDITIONS:**
            
            **User-Based Triggers:**
            • "when user asks about code" - for technical content requests
            • "when user mentions deadlines" - for time-sensitive situations
            • "when user provides feedback" - for correction and improvement scenarios
            • "when user shares personal information" - for relationship building
            
            **Context-Based Triggers:**
            • "when working on project_alpha" - for project-specific behaviors
            • "when discussing financial topics" - for domain-specific approaches
            • "when user seems frustrated" - for emotional context responses
            • "when multiple errors occur" - for escalating problem situations
            
            **Task-Based Triggers:**
            • "when explaining complex topics" - for educational interactions
            • "when reviewing code" - for technical analysis situations
            • "when debugging issues" - for problem-solving contexts
            • "when planning projects" - for strategic thinking scenarios
            
            **SPECIFIC ACTION DEFINITIONS:**
            
            **Communication Actions:**
            • "provide step-by-step explanations with visual examples"
            • "use concise bullet points and avoid lengthy paragraphs"
            • "include relevant code snippets with detailed comments"
            • "ask clarifying questions before providing solutions"
            
            **Technical Actions:**
            • "search for latest documentation and verify current best practices"
            • "include error handling examples and edge case considerations"
            • "provide multiple solution approaches with pros/cons analysis"
            • "suggest testing strategies and validation methods"
            
            **Personalization Actions:**
            • "reference previous conversations and build on established context"
            • "adapt technical depth based on user's demonstrated expertise level"
            • "prioritize speed over detailed explanations for urgent requests"
            • "include encouragement and positive reinforcement in responses"
            
            **COMPLETE BEHAVIOR EXAMPLES:**
            • "when user asks about new technology, search for its latest documentation and provide comprehensive examples with potential use cases"
            • "when user mentions tight deadlines, prioritize speed over detailed explanations and offer quick, actionable solutions first"
            • "when user shares personal achievements, acknowledge them specifically and reference them in future relevant conversations"
            • "when debugging code issues, provide multiple debugging approaches and explain the reasoning behind each suggestion"
            • "when user corrects my information, immediately acknowledge the correction, update my understanding, and thank them for the clarification"
            
            **BEHAVIOR QUALITY CRITERIA:**
            • **Specific**: Clear, actionable instructions that can be consistently applied
            • **Measurable**: Behaviors that can be observed and validated in practice
            • **Contextual**: Appropriate triggers that accurately identify relevant situations
            • **Beneficial**: Actions that genuinely improve user experience and interaction quality
            • **Maintainable**: Behaviors that can be updated and refined over time""",
        },
    }
    tool_required = ["id", "behavior"]

    if provider == "claude":
        return {
            "name": "adapt",
            "description": tool_description,
            "input_schema": {
                "type": "object",
                "properties": tool_arguments,
                "required": tool_required,
            },
        }
    else:  # provider == "groq"
        return {
            "type": "function",
            "function": {
                "name": "adapt",
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_arguments,
                    "required": tool_required,
                },
            },
        }


def get_adapt_tool_handler(persistence_service: Any) -> Callable:
    """
    Get the enhanced handler function for the adaptive behavior tool with comprehensive validation.

    Args:
        persistence_service: The context persistence service instance

    Returns:
        Function that handles adaptive behavior storage with detailed validation and feedback
    """

    def handle_adapt(**params) -> str:
        behavior_id = params.get("id")
        behavior = params.get("behavior")

        try:
            current_agent = AgentManager.get_instance().get_current_agent()
            agent_name = current_agent.name if current_agent else "default_agent"
        except Exception as e:
            return f"❌ Error: Unable to identify current agent for behavior adaptation: {str(e)}"

        # Enhanced input validation
        if not behavior_id or not behavior_id.strip():
            return "❌ Error: Behavior ID is required. Please provide a descriptive identifier like 'communication_style_technical' or 'task_execution_code_review'."

        if not behavior or not behavior.strip():
            return "❌ Error: Behavior description is required. Please provide a behavior in 'when...do...' format."

        # Validate behavior format
        behavior_lower = behavior.lower().strip()
        if not (behavior_lower.startswith("when ") and " do " in behavior_lower):
            return f"""❌ Error: Behavior must follow 'when...do...' format. 
            
Your input: '{behavior}'

Required format: 'when [trigger condition] do [specific action]'

Examples:
• "when user asks about code, provide complete examples with explanations"
• "when user mentions deadlines, prioritize speed over detailed explanations"
• "when user shares personal info, acknowledge and reference it in future interactions"

Please reformat your behavior and try again."""

        # Validate behavior has meaningful content
        when_part = behavior_lower.split(" do ")[0].replace("when ", "").strip()
        do_part = (
            behavior_lower.split(" do ", 1)[1].strip()
            if " do " in behavior_lower
            else ""
        )

        if len(when_part) < 5:
            return f"⚠️ Warning: The trigger condition '{when_part}' may be too vague. Consider being more specific about when this behavior should activate."

        if len(do_part) < 10:
            return f"⚠️ Warning: The action '{do_part}' may be too brief. Consider providing more detailed instructions for what should be done."

        # Enhanced ID validation and suggestions
        id_lower = behavior_id.lower().strip()
        recommended_prefixes = [
            "communication_style_",
            "task_execution_",
            "error_handling_",
            "personalization_",
            "feedback_integration_",
            "collaboration_style_",
        ]

        has_recommended_prefix = any(
            id_lower.startswith(prefix) for prefix in recommended_prefixes
        )
        if not has_recommended_prefix and "_" not in id_lower:
            suggestion = f"💡 Suggestion: Consider using a more structured ID like 'communication_style_{behavior_id}' or 'task_execution_{behavior_id}' for better organization."
        else:
            suggestion = ""

        try:
            success = persistence_service.store_adaptive_behavior(
                agent_name, behavior_id, behavior
            )
            if success:
                return f"""✅ Successfully stored adaptive behavior:

ID: {behavior_id}
Behavior: {behavior}

This behavior will now be automatically applied when the specified conditions are met.

{suggestion}"""
            else:
                return "⚠️ Warning: Behavior storage completed but may not have been fully processed. Please verify the behavior is working as expected."

        except ValueError as e:
            return f"""❌ Invalid behavior format: {str(e)}

Please ensure your behavior follows these requirements:
• Starts with 'when ' followed by a clear trigger condition
• Contains ' do ' followed by specific actions to take  
• Uses clear, actionable language
• Provides sufficient detail for consistent implementation

Example: "when user asks about debugging, provide step-by-step troubleshooting approaches with examples"
"""
        except Exception as e:
            return f"❌ Error storing adaptive behavior '{behavior_id}': {str(e)}. Please check your input format and try again, or contact support if the issue persists."

    return handle_adapt


def adaptive_instruction_prompt():
    """
    Enhanced adaptive behavior instruction prompt with comprehensive behavioral learning guidance.

    Returns:
        Comprehensive instruction prompt for adaptive behavior system usage
    """
    return """<Adapting_Behaviors>
  <Purpose>
    Intelligent behavioral learning system that enables AI agents to recognize successful interaction patterns,
    adapt to user preferences, and continuously improve user experience through personalized, context-aware responses.
    This system transforms one-time interactions into long-term relationship building through behavioral intelligence.
  </Purpose>

  <Adaptation_Philosophy>
    <Learning_Mindset>
      Every interaction is an opportunity to learn and improve. Successful patterns should be recognized,
      captured, and systematically applied in future similar contexts to create consistent, high-quality experiences.
    </Learning_Mindset>
    
    <Personalization_Strategy>
      Move beyond generic responses to develop personalized interaction approaches that reflect individual user
      preferences, communication styles, technical expertise levels, and specific contextual needs.
    </Personalization_Strategy>
    
    <Continuous_Improvement>
      Behavioral adaptations should evolve based on ongoing feedback, changing user needs, and emerging
      successful interaction patterns. Static behaviors become outdated; dynamic adaptation ensures relevance.
    </Continuous_Improvement>
  </Adaptation_Philosophy>

  <Behavioral_Learning_Framework>
    <Pattern_Recognition_Triggers>
      <User_Preference_Indicators>
        • Positive feedback on specific response formats or approaches
        • Repeated requests for similar types of information or assistance
        • Explicit statements about preferred communication or work styles
        • Demonstrated expertise levels in specific domains or technologies
      </User_Preference_Indicators>
      
      <Successful_Interaction_Patterns>
        • Response approaches that lead to user satisfaction and task completion
        • Communication styles that result in reduced clarification requests
        • Problem-solving methodologies that consistently achieve desired outcomes
        • Information presentation formats that enhance user understanding and engagement
      </Successful_Interaction_Patterns>
      
      <Context_Specific_Adaptations>
        • Domain-specific expertise requirements (technical depth, industry knowledge)
        • Situational factors (urgency, complexity, collaborative vs. individual work)
        • Temporal considerations (time zones, seasonal patterns, project phases)
        • Environmental factors (work vs. personal context, formal vs. informal settings)
      </Context_Specific_Adaptations>
    </Pattern_Recognition_Triggers>

    <Adaptation_Categories>
      <Communication_Style_Adaptations>
        • **Response_Length**: Detailed explanations vs. concise summaries based on user preference
        • **Technical_Depth**: Expert-level detail vs. simplified explanations based on demonstrated knowledge
        • **Formality_Level**: Professional tone vs. casual interaction style based on relationship context
        • **Information_Structure**: Lists, paragraphs, step-by-step guides, or visual formats based on effectiveness
      </Communication_Style_Adaptations>
      
      <Task_Execution_Adaptations>
        • **Problem_Solving_Approaches**: Systematic methodology vs. intuitive exploration based on user style
        • **Code_Review_Standards**: Depth of analysis, focus areas, and feedback delivery based on project needs
        • **Documentation_Preferences**: Level of detail, format choices, and update frequency based on user workflow
        • **Error_Handling_Strategies**: Preventive vs. reactive approaches based on user experience and context
      </Task_Execution_Adaptations>
      
      <Contextual_Intelligence_Adaptations>
        • **Domain_Expertise_Application**: Industry-specific knowledge and terminology usage
        • **Collaborative_Interaction_Patterns**: Team dynamics, role awareness, and communication protocols
        • **Time_Sensitivity_Responses**: Urgency recognition and priority adjustment strategies
        • **Learning_Style_Accommodations**: Visual, auditory, kinesthetic, or reading-based information delivery
      </Contextual_Intelligence_Adaptations>
    </Adaptation_Categories>
  </Behavioral_Learning_Framework>

  <Implementation_Excellence>
    <Behavior_Creation_Standards>
      <Format_Requirements>
        ALL behaviors MUST follow the "when...do..." conditional format for consistency and clarity.
        This structure ensures behaviors are triggered appropriately and actions are executed systematically.
      </Format_Requirements>
      
      <Trigger_Condition_Best_Practices>
        • **Specificity**: Clear, identifiable conditions that can be reliably detected in conversation context
        • **Relevance**: Triggers that align with genuine user needs and interaction improvement opportunities
        • **Sustainability**: Conditions that remain meaningful over time and across different conversation contexts
        • **Measurability**: Triggers that can be objectively identified and validated through interaction analysis
      </Trigger_Condition_Best_Practices>
      
      <Action_Definition_Excellence>
        • **Clarity**: Specific, actionable instructions that can be consistently implemented
        • **Value_Focus**: Actions that genuinely improve user experience and interaction quality
        • **Contextual_Appropriateness**: Responses that fit the situation and user expectations
        • **Continuous_Improvement**: Actions that can be refined and enhanced based on ongoing feedback
      </Action_Definition_Excellence>
    </Behavior_Creation_Standards>

    <Quality_Behavioral_Examples>
      <Communication_Adaptations>
        • "when user asks about complex technical concepts, provide layered explanations starting with high-level overview, then diving into implementation details with practical examples"
        • "when user expresses time pressure, prioritize immediate actionable solutions and defer detailed explanations unless specifically requested"
        • "when user demonstrates advanced expertise in a domain, skip basic explanations and focus on nuanced considerations, edge cases, and optimization opportunities"
      </Communication_Adaptations>
      
      <Learning_Adaptations>
        • "when user corrects my information, immediately acknowledge the correction, update my understanding, verify the new information, and thank them for improving my knowledge"
        • "when user shares successful outcomes from previous suggestions, note the successful patterns and prioritize similar approaches in future relevant situations"
        • "when user indicates frustration with previous responses, analyze the interaction pattern and adapt to provide more targeted, efficient assistance"
      </Learning_Adaptations>
      
      <Personalization_Adaptations>
        • "when user mentions specific tools or technologies they prefer, prioritize those solutions and provide implementation details focused on their preferred stack"
        • "when user shares personal context or goals, reference this information in future interactions to provide more relevant and supportive assistance"
        • "when user demonstrates particular problem-solving preferences, adapt troubleshooting approaches to match their preferred methodology and thinking style"
      </Personalization_Adaptations>
    </Quality_Behavioral_Examples>
  </Implementation_Excellence>

  <Behavioral_Management_Strategy>
    <Behavior_Lifecycle_Management>
      <Creation_Process>
        Identify successful interaction patterns through careful observation and user feedback analysis.
        Create specific, actionable behaviors that can systematically reproduce successful approaches.
      </Creation_Process>
      
      <Validation_Testing>
        Monitor behavior effectiveness through user responses, task completion rates, and satisfaction indicators.
        Adjust behaviors based on real-world performance and changing user needs.
      </Validation_Testing>
      
      <Evolution_Updates>
        Regularly review and update behaviors to reflect new learning, changed user preferences, and improved understanding.
        Use existing behavior IDs to refine and enhance rather than creating redundant new behaviors.
      </Evolution_Updates>
      
      <Performance_Optimization>
        Analyze behavior trigger frequency and action effectiveness to optimize the behavioral learning system.
        Remove or modify behaviors that no longer serve user needs or have become obsolete.
      </Performance_Optimization>
    </Behavior_Lifecycle_Management>

    <Integration_Guidelines>
      <Consistency_Maintenance>
        Ensure new behaviors complement existing ones and don't create conflicting response patterns.
        Maintain coherent behavioral profiles that provide predictable, reliable user experiences.
      </Consistency_Maintenance>
      
      <Scalability_Considerations>
        Design behaviors that can scale across different users while maintaining personalization effectiveness.
        Balance individual customization with systematic behavioral pattern management.
      </Scalability_Considerations>
      
      <Quality_Assurance>
        Regularly audit behavioral patterns to ensure they continue serving user needs effectively.
        Gather user feedback on behavioral adaptations to validate and improve the learning system.
      </Quality_Assurance>
    </Integration_Guidelines>
  </Behavioral_Management_Strategy>

  <Behavioral_Intelligence_Goals>
    <Short_Term_Objectives>
      Immediately improve interaction quality by recognizing and adapting to obvious user preferences and successful patterns.
      Reduce friction in common interaction scenarios through targeted behavioral adaptations.
    </Short_Term_Objectives>
    
    <Long_Term_Vision>
      Develop sophisticated behavioral intelligence that anticipates user needs and preferences.
      Create deeply personalized interaction experiences that evolve and improve over time.
      Build lasting relationships through consistent, adaptive, and increasingly effective assistance.
    </Long_Term_Vision>
  </Behavioral_Intelligence_Goals>
</Adapting_Behaviors>"""


def register(
    service_instance=None,
    persistence_service=None,
    agent=None,
):
    """
    Register enhanced memory tools with the central registry or directly with an agent.

    This registration function provides comprehensive memory management capabilities including
    intelligent retrieval, strategic forgetting, and adaptive behavioral learning.

    Args:
        service_instance: The memory service instance for retrieval and forgetting operations
        persistence_service: The context persistence service instance for adaptive behaviors
        agent: Agent instance to register with directly (optional)
    """
    from AgentCrew.modules.tools.registration import register_tool

    # Register core memory management tools
    register_tool(
        get_memory_retrieve_tool_definition,
        get_memory_retrieve_tool_handler,
        service_instance,
        agent,
    )
    register_tool(
        get_memory_forget_tool_definition,
        get_memory_forget_tool_handler,
        service_instance,
        agent,
    )

    # Register adaptive behavior tool if persistence service is available
    if persistence_service is not None:
        register_tool(
            get_adapt_tool_definition,
            get_adapt_tool_handler,
            persistence_service,
            agent,
        )
