//------------------------------------------------------------------------------
// <auto-generated>
//     This code was generated from a template.
//
//     Manual changes to this file may cause unexpected behavior in your application.
//     Manual changes to this file will be overwritten if the code is regenerated.
// </auto-generated>
//------------------------------------------------------------------------------

namespace ConfigMan
{
    using System;
    using System.Collections.Generic;
    
    public partial class Documentation
    {
        public int DocumentID { get; set; }
        public int ComponentID { get; set; }
        public string InstallationText { get; set; }
        public Nullable<System.DateTime> LastRevisionDate { get; set; }
    
        public virtual Component Component { get; set; }
    }
}
