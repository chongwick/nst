require 'prism'
require 'json'

# Function to convert a Prism node to a hash suitable for JSON
def node_to_hash(node)
  return nil unless node

  # Extract node type and location
  hash = {
    type: node.type,
    location: {
      start_line: node.location.start_line,
      start_column: node.location.start_column,
      end_line: node.location.end_line,
      end_column: node.location.end_column
    }
  }

  # Get node-specific fields using instance variables (bypassing deconstruct_keys)
  node.instance_variables.each do |ivar|
    # Skip internal fields like @type and @location
    next if ivar == :@type || ivar == :@location

    # Convert instance variable name to field name (e.g., :@body -> :body)
    field_name = ivar.to_s.sub(/^@/, '').to_sym
    value = node.instance_variable_get(ivar)

    # Recursively convert child nodes or arrays of nodes
    if value.is_a?(Array)
      hash[field_name] = value.map { |v| v.is_a?(Prism::Node) ? node_to_hash(v) : v }.compact
    elsif value.is_a?(Prism::Node)
      hash[field_name] = node_to_hash(value)
    else
      hash[field_name] = value
    end
  end

  hash
end

# Main function to parse source and convert to JSON
def ast_to_json(source, include_comments: false, input_file: nil)
  # Parse the source code
  result = input_file ? Prism.parse_file(input_file) : Prism.parse(source)

  # Prepare the output hash
  output = {
    success: result.success?,
    ast: result.success? ? node_to_hash(result.value) : nil,
    errors: result.errors.map { |e|
      {
        message: e.message,
        location: {
          start_line: e.location.start_line,
          start_column: e.location.start_column,
          end_line: e.location.end_line,
          end_column: e.location.end_column
        }
      }
    },
    warnings: result.warnings.map { |w|
      {
        message: w.message,
        location: {
          start_line: w.location.start_line,
          start_column: w.location.start_column,
          end_line: w.location.end_line,
          end_column: w.location.end_column
        }
      }
    }
  }

  # Optionally include comments
  #if include_comments
  #  output[:comments] = result.comments.map do |c|
  #    {
  #      type: c.class.name.split('::').last,
  #      content: c.to_s,
  #      location: {
  #        start_line: c.location.start_line,
  #        start_column: c.location.start_column,
  #        end_line: c.location.end_line,
  #        end_column: c.location.end_column
  #      }
  #    }
  #  end
  #end

  # Convert to JSON
  JSON.pretty_generate(output)
end

# Example usage
if ARGV.empty?
  # Example source code if no file is provided
  source = <<~RUBY
    # A sample class
    class Example
      def hello(name)
        puts "Hello, \#{name}!"
      end
    end
  RUBY

  puts ast_to_json(source, include_comments: true)
else
  # Read from file if provided
  input_file = ARGV[0]
  unless File.exist?(input_file)
    puts "Error: File '#{input_file}' not found."
    exit 1
  end
  #puts ast_to_json(nil, include_comments: true, input_file: input_file)
  File.write('ast.json', ast_to_json(nil, include_comments: true, input_file: input_file))
end

# Optional: Save to file
#File.write('ast.json', ast_to_json(source, include_comments: true))
