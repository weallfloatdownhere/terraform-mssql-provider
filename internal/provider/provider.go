package mssql

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"

	"github.com/hashicorp/terraform-plugin-framework/provider"
	"github.com/hashicorp/terraform-plugin-framework/provider/schema"
	"github.com/hashicorp/terraform-plugin-framework/resource"
	"github.com/hashicorp/terraform-plugin-framework/types"
	"github.com/microsoft/go-mssqldb"
)

var _ provider.Provider = &MSSQLProvider{}

// Define Provider Structure
type MSSQLProvider struct{}

// Provider Factory
func NewProvider() provider.Provider {
	return &MSSQLProvider{}
}

// Schema for Provider
func (p *MSSQLProvider) Metadata(_ context.Context, _ provider.MetadataRequest, resp *provider.MetadataResponse) {
	resp.TypeName = "mssql"
}

func (p *MSSQLProvider) Schema(_ context.Context, _ provider.SchemaRequest, resp *provider.SchemaResponse) {
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
			"use_managed_identity": schema.BoolAttribute{
				Optional:    true,
				Description: "Use Azure Managed Identity for authentication.",
			},
		},
	}
}

// Configure Provider
func (p *MSSQLProvider) Configure(ctx context.Context, req provider.ConfigureRequest, resp *provider.ConfigureResponse) {
	var config struct {
		Server             string `tfsdk:"server"`
		Database           string `tfsdk:"database"`
		UseManagedIdentity bool   `tfsdk:"use_managed_identity"`
	}

	diags := req.Config.Get(ctx, &config)
	resp.Diagnostics.Append(diags...)
	if resp.Diagnostics.HasError() {
		return
	}

	var connString string

	if config.UseManagedIdentity {
		token, err := getManagedIdentityToken()
		if err != nil {
			resp.Diagnostics.AddError("Managed Identity Authentication Failed", err.Error())
			return
		}
		connString = fmt.Sprintf("server=%s;database=%s;azure token=%s", config.Server, config.Database, token)
	} else {
		resp.Diagnostics.AddError("Authentication Error", "Only Managed Identity authentication is supported.")
		return
	}

	db, err := sql.Open("sqlserver", connString)
	if err != nil {
		resp.Diagnostics.AddError("Database Connection Failed", err.Error())
		return
	}

	resp.DataSourceData = db
	resp.ResourceData = db
}

// Get Azure Managed Identity Token
func getManagedIdentityToken() (string, error) {
	identityURL := "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://database.windows.net/"
	req, err := http.NewRequest("GET", identityURL, nil)
	if err != nil {
		return "", err
	}

	req.Header.Set("Metadata", "true")
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	var data map[string]string
	err = json.Unmarshal(body, &data)
	if err != nil {
		return "", err
	}

	return data["access_token"], nil
}
