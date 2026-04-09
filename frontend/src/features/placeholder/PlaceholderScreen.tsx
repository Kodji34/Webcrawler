import PendingActionsOutlinedIcon from '@mui/icons-material/PendingActionsOutlined'
import {
  Box,
  Chip,
  Grid,
  List,
  ListItem,
  Paper,
  Stack,
  Typography,
} from '@mui/material'
import { useTranslation } from 'react-i18next'

type PlaceholderScreenProps = {
  pageKey: 'researchQueue' | 'collections' | 'schedules' | 'settings'
}

export function PlaceholderScreen({ pageKey }: PlaceholderScreenProps) {
  const { t } = useTranslation()
  const checklist = t(`pages.${pageKey}.checklist`, {
    returnObjects: true,
  }) as string[]

  return (
    <Grid container spacing={2.5}>
      <Grid size={{ xs: 12, lg: 7 }}>
        <Paper className="rise-in" sx={{ p: 3.25 }}>
          <Stack spacing={2.5}>
            <Box>
              <Chip label={t('pages.phaseChip')} color="secondary" size="small" />
              <Typography variant="h3" sx={{ mt: 1.5, mb: 1 }}>
                {t(`pages.${pageKey}.title`)}
              </Typography>
              <Typography color="text.secondary">
                {t(`pages.${pageKey}.description`)}
              </Typography>
            </Box>
            <List sx={{ p: 0 }}>
              {checklist.map((item) => (
                <ListItem key={item} sx={{ px: 0 }}>
                  <PendingActionsOutlinedIcon
                    fontSize="small"
                    sx={{ color: 'secondary.main', mr: 1.5 }}
                  />
                  <Typography>{item}</Typography>
                </ListItem>
              ))}
            </List>
          </Stack>
        </Paper>
      </Grid>
      <Grid size={{ xs: 12, lg: 5 }}>
        <Paper className="rise-in" sx={{ p: 3.25, height: '100%' }}>
          <Stack spacing={2}>
            <Typography variant="h5">{t(`pages.${pageKey}.handoffTitle`)}</Typography>
            <Typography color="text.secondary">
              {t(`pages.${pageKey}.handoffBody`)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {t('pages.phaseBoundary')}
            </Typography>
          </Stack>
        </Paper>
      </Grid>
    </Grid>
  )
}
