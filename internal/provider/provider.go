package provider

import (
    "context"
    "os"
   
    "github.com/hashicorp-demoapp/hashicups-client-go"

    "github.com/hashicorp/terraform-plugin-framework/datasource"
    "github.com/hashicorp/terraform-plugin-framework/path"
    "github.com/hashicorp/terraform-plugin-framework/provider"
    "github.com/hashicorp/terraform-plugin-framework/provider/schema"
    "github.com/hashicorp/terraform-plugin-framework/resource"
    "github.com/hashicorp/terraform-plugin-framework/types"
  )
  

// Ensure the implementation satisfies the expected interfaces.
var (
    _ provider.Provider = &MssqlProvider{}
)

// New is a helper function to simplify provider server and testing implementation.
func New(version string) func() provider.Provider {
    return func() provider.Provider {
        return &MssqlProvider{
            version: version,
        }
    }
}

// MssqlProvider is the provider implementation.
type MssqlProvider struct {
    version string
}

// MssqlProviderModel maps provider schema data to a Go type.
type MssqlProviderModel struct {
	Server   string `tfsdk:"server"`
	Database string `tfsdk:"database"`
	Username string `tfsdk:"username"`
	Password string `tfsdk:"password"`
}

// Metadata returns the provider type name.
func (p *MssqlProvider) Metadata(_ context.Context, _ provider.MetadataRequest, resp *provider.MetadataResponse) {
    resp.TypeName = "hashicups"
    resp.Version = p.version
}

// Schema defines the provider-level schema for configuration data.
func (p *MssqlProvider) Schema(_ context.Context, _ provider.SchemaRequest, resp *provider.SchemaResponse) {
    resp.Schema = schema.Schema{
        Attributes: map[string]schema.Attribute{
			"server": schema.StringAttribute{
				Required:    true,
				Description: "The Azure MSSQL Server name.",
			},
			"database": schema.StringAttribute{
				Required:    true,
				Description: "The MSSQL database to connect to.",
			},
			"username": schema.StringAttribute{
				Required:    true,
				Description: "The database username.",
			},
			"password": schema.StringAttribute{
				Required:    true,
				Sensitive:   true,
				Description: "The database password.",
			},
        },
    }
}

// Configure prepares a HashiCups API client for data sources and resources.
func (p *MssqlProvider) Configure(ctx context.Context, req provider.ConfigureRequest, resp *provider.ConfigureResponse) { 
    var config MssqlProviderModel
    
	diags := req.Config.Get(ctx, &config)
    
	resp.Diagnostics.Append(diags...)

    if resp.Diagnostics.HasError() {
        return
    }

    if config.Server.IsUnknown() {
        resp.Diagnostics.AddAttributeError(
            path.Root("server"),
            "Unknown MSSQL Server",
            "The provider cannot create the MSSQL API client as there is an unknown configuration value for the MSSQL Server. "+
                "Either target apply the source of the value first, set the value statically in the configuration, or use the MSSQL_SERVER environment variable.",
        )
    }

    if config.Database.IsUnknown() {
        resp.Diagnostics.AddAttributeError(
            path.Root("database"),
            "Unknown MSSQL Database",
            "The provider cannot create the MSSQL API client as there is an unknown configuration value for the MSSQL Database. "+
                "Either target apply the source of the value first, set the value statically in the configuration, or use the MSSQL_DATABASE environment variable.",
        )
    }


    if config.Username.IsUnknown() {
        resp.Diagnostics.AddAttributeError(
            path.Root("username"),
            "Unknown MSSQL Username",
            "The provider cannot create the MSSQL API client as there is an unknown configuration value for the MSSQL Username. "+
                "Either target apply the source of the value first, set the value statically in the configuration, or use the MSSQL_USERNAME environment variable.",
        )
    }

    if config.Password.IsUnknown() {
        resp.Diagnostics.AddAttributeError(
            path.Root("password"),
            "Unknown MSSQL Password",
            "The provider cannot create the MSSQL API client as there is an unknown configuration value for the MSSQL Password. "+
                "Either target apply the source of the value first, set the value statically in the configuration, or use the MSSQL_PASSWORD environment variable.",
        )
    }

    if resp.Diagnostics.HasError() {
        return
    }

    // Default values to environment variables, but override
    // with Terraform configuration value if set.

    server   := os.Getenv("MSSQL_SERVER")
	database := os.Getenv("MSSQL_DATABASE")
    username := os.Getenv("MSSQL_USERNAME")
    password := os.Getenv("MSSQL_PASSWORD")

    if !config.Server.IsNull() {
        server = config.Server.ValueString()
    }

	if !config.Database.IsNull() {
        database = config.Server.ValueString()
    }

    if !config.Username.IsNull() {
        username = config.Username.ValueString()
    }

    if !config.Password.IsNull() {
        password = config.Password.ValueString()
    }

    // If any of the expected configurations are missing, return
    // errors with provider-specific guidance.

    if server == "" {
        resp.Diagnostics.AddAttributeError(
            path.Root("server"),
            "Missing MSSQL Server",
            "The provider cannot create the MSSQL API client as there is a missing or empty value for the MSSQL Server. "+
                "Set the host value in the configuration or use the MSSQL_SERVER environment variable. "+
                "If either is already set, ensure the value is not empty.",
        )
    }

	if database == "" {
        resp.Diagnostics.AddAttributeError(
            path.Root("database"),
            "Missing MSSQL Server",
            "The provider cannot create the MSSQL client as there is a missing or empty value for the MSSQL Database. "+
                "Set the host value in the configuration or use the MSSQL_DATABASE environment variable. "+
                "If either is already set, ensure the value is not empty.",
        )
    }

    if username == "" {
        resp.Diagnostics.AddAttributeError(
            path.Root("username"),
            "Missing MSSQL Username",
            "The provider cannot create the MSSQL client as there is a missing or empty value for the MSSQL Username. "+
                "Set the username value in the configuration or use the MSSQL_USERNAME environment variable. "+
                "If either is already set, ensure the value is not empty.",
        )
    }

    if password == "" {
        resp.Diagnostics.AddAttributeError(
            path.Root("password"),
            "Missing MSSQL Password",
            "The provider cannot create the MSSQL API client as there is a missing or empty value for the MSSQL Password. "+
                "Set the password value in the configuration or use the MSSQL_PASSWORD environment variable. "+
                "If either is already set, ensure the value is not empty.",
        )
    }

    if resp.Diagnostics.HasError() {
        return
    }

    // Create a new HashiCups client using the configuration values
    client, err := hashicups.NewClient(&server, &database, &username, &password)

    if err != nil {
        resp.Diagnostics.AddError(
            "Unable to Create HashiCups API Client",
            "An unexpected error occurred when creating the HashiCups API client. "+
                "If the error is not clear, please contact the provider developers.\n\n"+
                "HashiCups Client Error: "+err.Error(),
        )
        return
    }

    // Make the HashiCups client available during DataSource and Resource
    // type Configure methods.
    resp.DataSourceData = client
    resp.ResourceData = client
}

// DataSources defines the data sources implemented in the provider.
func (p *MssqlProvider) DataSources(_ context.Context) []func() datasource.DataSource {
    return nil
}

// Resources defines the resources implemented in the provider.
func (p *MssqlProvider) Resources(_ context.Context) []func() resource.Resource {
    return nil
}
