package mssql

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/hashicorp/terraform-plugin-framework/resource"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema"
	"github.com/hashicorp/terraform-plugin-framework/types"
)

var _ resource.Resource = &MSSQLQueryResource{}

// Query Resource Structure
type MSSQLQueryResource struct {
	db *sql.DB
}

// New Query Resource
func NewMSSQLQueryResource(db *sql.DB) resource.Resource {
	return &MSSQLQueryResource{db: db}
}

// Resource Metadata
func (r *MSSQLQueryResource) Metadata(_ context.Context, _ resource.MetadataRequest, resp *resource.MetadataResponse) {
	resp.TypeName = "mssql_query"
}

// Define Query Schema
func (r *MSSQLQueryResource) Schema(_ context.Context, _ resource.SchemaRequest, resp *resource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Attributes: map[string]schema.Attribute{
			"query": schema.StringAttribute{
				Required:    true,
				Description: "SQL query to execute.",
			},
			"result": schema.StringAttribute{
				Computed:    true,
				Description: "Query execution result.",
			},
		},
	}
}

// Execute Query
func (r *MSSQLQueryResource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
	var plan struct {
		Query types.String `tfsdk:"query"`
	}
	req.Plan.Get(ctx, &plan)

	_, err := r.db.Exec(plan.Query.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("SQL Execution Failed", err.Error())
		return
	}

	resp.State.Set(ctx, &plan)
}

// No Read/Delete Operations Required
func (r *MSSQLQueryResource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {}
func (r *MSSQLQueryResource) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {}
