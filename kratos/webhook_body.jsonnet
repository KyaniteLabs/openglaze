local identity = ctx.identity;

{
  identity_id: identity.id,
  email: identity.traits.email,
  studio_name: identity.traits.studio_name,
  template_id: identity.traits.template_id,
  created_at: identity.created_at
}
