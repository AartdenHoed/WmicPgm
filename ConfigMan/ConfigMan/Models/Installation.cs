using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;
using System.Web;

namespace ConfigMan.Models
{
    public partial class Installation
    {
        [NotMapped]
        public string Vendor;
        [NotMapped]
        public String Component;
    }
}