import DashboardCustomizeOutlinedIcon from '@mui/icons-material/DashboardCustomizeOutlined'
import EventRepeatOutlinedIcon from '@mui/icons-material/EventRepeatOutlined'
import FeedOutlinedIcon from '@mui/icons-material/FeedOutlined'
import LibraryBooksOutlinedIcon from '@mui/icons-material/LibraryBooksOutlined'
import PictureAsPdfOutlinedIcon from '@mui/icons-material/PictureAsPdfOutlined'
import ScienceOutlinedIcon from '@mui/icons-material/ScienceOutlined'
import SettingsSuggestOutlinedIcon from '@mui/icons-material/SettingsSuggestOutlined'
import TravelExploreOutlinedIcon from '@mui/icons-material/TravelExploreOutlined'
import type { SvgIconComponent } from '@mui/icons-material'

export type NavigationItem = {
  key: string
  path: string
  icon: SvgIconComponent
}

export const navigationItems: NavigationItem[] = [
  {
    key: 'dashboard',
    path: '/',
    icon: DashboardCustomizeOutlinedIcon,
  },
  {
    key: 'scientificSearch',
    path: '/scientific-search',
    icon: ScienceOutlinedIcon,
  },
  {
    key: 'pdfWorkspace',
    path: '/pdf-workspace',
    icon: PictureAsPdfOutlinedIcon,
  },
  {
    key: 'webImports',
    path: '/web-imports',
    icon: FeedOutlinedIcon,
  },
  {
    key: 'researchQueue',
    path: '/research-queue',
    icon: TravelExploreOutlinedIcon,
  },
  {
    key: 'collections',
    path: '/collections',
    icon: LibraryBooksOutlinedIcon,
  },
  {
    key: 'schedules',
    path: '/schedules',
    icon: EventRepeatOutlinedIcon,
  },
  {
    key: 'settings',
    path: '/settings',
    icon: SettingsSuggestOutlinedIcon,
  },
]
